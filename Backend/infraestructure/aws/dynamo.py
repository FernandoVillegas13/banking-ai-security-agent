import boto3
from datetime import datetime
import json
from decimal import Decimal
from typing import Optional, Dict, Any
import os

class DynamoService:

    def __init__(self, table_name: str = "bcp_transactions", region_name: str = "us-east-1"):
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name
    
    def _serialize_to_dict(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        elif hasattr(obj, 'model_dump'):
            return self._serialize_to_dict(obj.model_dump())
        elif hasattr(obj, 'dict'):
            return self._serialize_to_dict(obj.dict())
        elif isinstance(obj, dict):
            return {k: self._serialize_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_to_dict(item) for item in obj]
        elif isinstance(obj, tuple):
            return [self._serialize_to_dict(item) for item in obj]
        elif isinstance(obj, set):
            return [self._serialize_to_dict(item) for item in obj]
        return obj
    
    def _convert_floats_to_decimal(self, obj: Any) -> Any:
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimal(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimal(item) for item in obj]
        return obj
    
    def _convert_decimal_to_float(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: self._convert_decimal_to_float(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_decimal_to_float(item) for item in obj]
        return obj
    
    def save_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        try:
            item = self._serialize_to_dict(transaction_data)
            item['saved_at'] = datetime.utcnow().isoformat() + 'Z'
            item['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            
            item = self._convert_floats_to_decimal(item)
            
            self.table.put_item(Item=item)
            
            print(f"Transaction {transaction_data.get('transaction_id')} saved to DynamoDB")
            return True
            
        except Exception as e:
            print(f"Error saving transaction to DynamoDB: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(
                Key={'transaction_id': transaction_id}
            )
            
            if 'Item' in response:
                item = self._convert_decimal_to_float(response['Item'])
                return item
            else:
                print(f"Transaction {transaction_id} not found in DynamoDB")
                return None
                
        except Exception as e:
            print(f"Error retrieving transaction from DynamoDB: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_transaction(self, transaction_id: str, updates: Dict[str, Any]) -> bool:
        try:
            updates['updated_at'] = datetime.utcnow().isoformat() + 'Z'
            updates = self._convert_floats_to_decimal(updates)
            
            update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in updates.keys()])
            expr_attr_names = {f"#{k}": k for k in updates.keys()}
            expr_attr_values = {f":{k}": v for k, v in updates.items()}
            
            self.table.update_item(
                Key={'transaction_id': transaction_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            
            print(f"Transaction {transaction_id} updated in DynamoDB")
            return True
            
        except Exception as e:
            print(f"Error updating transaction in DynamoDB: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_transactions(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        try:
            if limit:
                response = self.table.scan(Limit=limit)
            else:
                response = self.table.scan()
            
            items = response.get('Items', [])
            
            while 'LastEvaluatedKey' in response and not limit:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            transactions = [self._convert_decimal_to_float(item) for item in items]
            return transactions
            
        except Exception as e:
            print(f"Error retrieving all transactions from DynamoDB: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

