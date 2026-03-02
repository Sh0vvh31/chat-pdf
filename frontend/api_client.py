import requests
import os
from typing import Dict, Any, List, Optional

# Docker-composeの内部ネットワーク向けURL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")

def login(username, password) -> Dict[str, Any]:
    res = requests.post(f"{API_BASE_URL}/users/login", json={"username": username, "password": password})
    res.raise_for_status()
    return res.json()

def register(username, password) -> Dict[str, Any]:
    res = requests.post(f"{API_BASE_URL}/users/register", json={"username": username, "password": password})
    res.raise_for_status()
    return res.json()

def upload_document(user_id: str, file_path: str, filename: str) -> Dict[str, Any]:
    with open(file_path, "rb") as f:
        # FastAPI expects file and user_id both as form data
        files = {"file": (filename, f, "application/pdf")}
        data = {"user_id": user_id}
        res = requests.post(f"{API_BASE_URL}/documents/upload", files=files, data=data)
        
        # 422 Unprocessable Entity or 400 Bad Request if validation fails
        if not res.ok:
            raise Exception(f"HTTP Error {res.status_code}: {res.text}")
            
        return res.json()

def create_thread(user_id: str, document_id: Optional[str] = None, title: str = "New Chat") -> Dict[str, Any]:
    data = {"user_id": user_id, "title": title}
    if document_id:
        data["document_id"] = document_id
    res = requests.post(f"{API_BASE_URL}/chat/threads", json=data)
    res.raise_for_status()
    return res.json()

def send_chat_message(user_id: str, thread_id: str, question: str, document_id: Optional[str] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
    data = {
        "user_id": user_id,
        "thread_id": thread_id,
        "question": question
    }
    if document_id:
        data["document_id"] = document_id
        
    if model_name:
        data["model_name"] = model_name
        
    res = requests.post(f"{API_BASE_URL}/chat/messages", json=data)
    res.raise_for_status()
    return res.json()

def get_thread_messages(thread_id: str) -> List[Dict[str, Any]]:
    res = requests.get(f"{API_BASE_URL}/chat/threads/{thread_id}/messages")
    res.raise_for_status()
    return res.json()
