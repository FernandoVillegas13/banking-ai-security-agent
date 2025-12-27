
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import pandas as pd
import os

DATABASE_URL = os.getenv("DATABASE_URL")

class DataBaseDeepFeel:

    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 10,
            },
            echo=False,
            pool_reset_on_return="rollback",
            isolation_level="AUTOCOMMIT",
            execution_options={"schema_translate_map": {None: "deepfeel"}}
        )