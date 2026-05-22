"""
src/storage/mongo.py
Funções para salvar os registros no MongoDB, apenas uma classe que pensei em usar no inicio 
agora estamos com firebase, mas mantive ela caso decida voltar
"""

from typing import List
from pymongo import MongoClient
from common.models import CommentRecord

def init_collection(mongo_url: str, db_name: str, collection: str):
    client = MongoClient(mongo_url)
    db = client[db_name]
    col = db[collection]
    col.create_index("classification")
    col.create_index("source_id")
    col.create_index([("extras.publishedAt", 1)])
    return col

def save_records(col, records: List[CommentRecord]):
    if not records:
        return
    payload = [r.to_dict() for r in records]
    col.insert_many(payload)
