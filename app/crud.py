from fastapi import FastAPI, HTTPException
from app.models import Item, ItemCreate
from app.database import get_firestore_client
from typing import List
from datetime import datetime, timezone
import json
import logging

# FirestoreとRedisの初期化
db = get_firestore_client()
collection_name = "test-collection"

app_name = "Firestore CRUD API"
version = "1.0.0"

def create_app() -> FastAPI:
    app = FastAPI(title=app_name, version=version)

    logging.basicConfig(level=logging.INFO)

    @app.post("/items", response_model=Item)
    def create_item(item: ItemCreate):
        try:
            # Firestoreにデータを保存
            doc_ref = db.collection(collection_name).document()
            data = item.dict()
            created_at = datetime.now(timezone.utc)
            data["created_at"] = created_at.isoformat() 
            doc_ref.set(data)

            return {"id": doc_ref.id, **data}
        except Exception as e:
            logging.error(f"Error creating item: {e}")
            raise HTTPException(status_code=500, detail="Failed to create item.")

    @app.get("/items/{item_id}", response_model=Item)
    def get_item(item_id: str):
        try:
            # Firestoreからデータを取得
            doc = db.collection(collection_name).document(item_id).get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Item not found")

            data = doc.to_dict()
            return {"id": doc.id, **data}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error retrieving item {item_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve item.")

    @app.get("/items", response_model=List[Item])
    def list_items():
        try:
            # Firestoreからデータを取得
            docs = db.collection(collection_name).stream()
            items = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            return items
        except Exception as e:
            logging.error(f"Error listing items: {e}")
            raise HTTPException(status_code=500, detail="Failed to list items.")

    @app.put("/items/{item_id}", response_model=Item)
    def update_item(item_id: str, item: ItemCreate):
        try:
            # Firestoreのドキュメントを更新
            doc_ref = db.collection(collection_name).document(item_id)
            if not doc_ref.get().exists:
                raise HTTPException(status_code=404, detail="Item not found")
    
            data = item.dict()
            updated_at = datetime.now(timezone.utc)
            data["updated_at"] = updated_at.isoformat() 
            doc_ref.update(data)
            # 更新前のcreated_atを取得
            doc = doc_ref.get()
            created_at = doc.to_dict().get("created_at")
            return {"id": item_id, "created_at": created_at, **data}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error updating item {item_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update item.")

    @app.delete("/items/{item_id}")
    def delete_item(item_id: str):
        try:
            # Firestoreのドキュメントを削除
            doc_ref = db.collection(collection_name).document(item_id)
            if not doc_ref.get().exists:
                raise HTTPException(status_code=404, detail="Item not found")
            doc_ref.delete()

            return {"message": "Item deleted successfully"}
        except HTTPException as he:
            raise he
        except Exception as e:
            logging.error(f"Error deleting item {item_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete item.")

    return app
