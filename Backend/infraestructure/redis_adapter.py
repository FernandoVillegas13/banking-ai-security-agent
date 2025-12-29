import redis
import os
import json
from datetime import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class RedisAdapter:
    def __init__(self):
        host = os.getenv("REDIS_HOST", "redis")
        port = int(os.getenv("REDIS_PORT", 6380))
        self.r = redis.Redis(host=host, port=port, db=0, decode_responses=True)
        self.HITL_QUEUE_KEY = "hitl:queue"
        self.HITL_DATA_PREFIX = "hitl:data:"

    def exists(self, key):
        return self.r.exists(key)
    
    def set(self, key, value, ex=None):
        self.r.set(key, value, ex=ex)
    
    # HITL Queue Methods
    def add_to_hitl_queue(self, transaction_id: str, transaction_data: dict):
        # Guardar datos completos en un hash
        print("Adding to HITL queue:", transaction_id, transaction_data)
        data_key = f"{self.HITL_DATA_PREFIX}{transaction_id}"
        print("Storing data key:", data_key)
        self.r.set(data_key, json.dumps(transaction_data, cls=DateTimeEncoder))
        # Agregar transaction_id a la cola
        self.r.lpush(self.HITL_QUEUE_KEY, transaction_id)
        print(f"Transaction {transaction_id} added to HITL queue")
        
    def get_pending_hitl_transactions(self) -> list:
        return self.r.lrange(self.HITL_QUEUE_KEY, 0, -1)
    
    def get_hitl_transaction(self, transaction_id: str) -> dict:
        data_key = f"{self.HITL_DATA_PREFIX}{transaction_id}"
        data = self.r.get(data_key)
        return json.loads(data) if data else None
    
    def update_hitl_decision(self, transaction_id: str, new_decision: str, reviewer_notes: str = "") -> bool:
        data_key = f"{self.HITL_DATA_PREFIX}{transaction_id}"
        data = self.get_hitl_transaction(transaction_id)
        
        if not data:
            return False
        
        # Actualizar decisión
        data['decision'] = new_decision
        data['reviewed_by_human'] = True
        data['reviewer_notes'] = reviewer_notes
        data['reviewed_at'] = str(datetime.now())
        
        # Guardar actualización
        self.r.set(data_key, json.dumps(data, cls=DateTimeEncoder))
        
        # Remover de la cola
        self.r.lrem(self.HITL_QUEUE_KEY, 0, transaction_id)
        
        return True
    
    def get_hitl_queue_length(self) -> int:
        return self.r.llen(self.HITL_QUEUE_KEY)