from infraestructure.redis_adapter import RedisAdapter
from typing import Dict, Any
import datetime

class HumanReviewQueue():

    def __init__(self, redis_adapter: RedisAdapter = None):
        self.redis = redis_adapter or RedisAdapter()
    
    async def escalate(self, state: Dict[str, Any]) -> Dict[str, Any]:      
        transaction_id = state.get('transaction_id')
        
        print(f"Transaction {transaction_id} being escalated to human review queue")
        
        self.redis.add_to_hitl_queue(transaction_id, {'transaction_id': transaction_id})
        
        print(f"Transaction {transaction_id} escalated to human review queue")
        
        return {
            'need_human_review': True,
            'hitl_status': 'escalated',
        }