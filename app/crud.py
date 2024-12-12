from fastapi import FastAPI, HTTPException
from app.models import Item, ItemCreate
from app.database import get_firestore_client
from typing import List
from datetime import datetime, timezone
import json

# FirestoreとRedisの初期化
db = get_firestore_client()
collection_name = "test-collection"

app_name = "Firestore CRUD API"
version = "1.0.0"

def create_app() -> FastAPI:
    app = FastAPI(title=app_name, version=version)

    @app.post("/items", response_model=Item)
    def create_item(item: ItemCreate):
        # Firestoreにデータを保存
        doc_ref = db.collection(collection_name).document()
        data = item.dict()
        created_at = datetime.now(timezone.utc)
        data["created_at"] = created_at.isoformat() 
        doc_ref.set(data)

        return {"id": doc_ref.id, **data}

    @app.get("/items/{item_id}", response_model=Item)
    def get_item(item_id: str):

        # Firestoreからデータを取得
        doc = db.collection(collection_name).document(item_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Item not found")

        data = doc.to_dict()
        return {"id": doc.id, **data}

    @app.get("/items", response_model=List[Item])
    def list_items():
        # Firestoreからデータを取得
        docs = db.collection(collection_name).stream()
        items = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        return items

    @app.put("/items/{item_id}", response_model=Item)
    def update_item(item_id: str, item: ItemCreate):
        # Firestoreのドキュメントを更新
        doc_ref = db.collection(collection_name).document(item_id)
        if not doc_ref.get().exists():
            raise HTTPException(status_code=404, detail="Item not found")

        data = item.dict()
        data["updated_at"] = datetime.utcnow()
        doc_ref.update(data)

        return {"id": item_id, **data}

    @app.delete("/items/{item_id}")
    def delete_item(item_id: str):
        # Firestoreのドキュメントを削除
        doc_ref = db.collection(collection_name).document(item_id)
        if not doc_ref.get().exists():
            raise HTTPException(status_code=404, detail="Item not found")
        doc_ref.delete()
        
        return {"message": "Item deleted successfully"}

    return app
