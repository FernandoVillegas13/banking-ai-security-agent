import json
from pathlib import Path
from domain.schema.schemas import UsualBehavior

class SearchUsual:

    def get_usual_behavior_by_customer_id(self, customer_id: str) -> UsualBehavior:

        db_path: str = "usual_behavior_db.json"

        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for record in data:
            if record.get("customer_id") == customer_id:
                return UsualBehavior(**record)
        return None