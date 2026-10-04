import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from app.rag.schema import SessionMessage, SessionHistoryResponse

class SessionStore:
    def __init__(self):
        # session_id -> list of SessionMessage
        self._store: Dict[str, List[SessionMessage]] = {}
        self._metadata: Dict[str, Dict[str, str]] = {}

    def get_history(self, session_id: str) -> SessionHistoryResponse:
        now_iso = datetime.now(timezone.utc).isoformat()
        messages = self._store.get(session_id, [])
        meta = self._metadata.get(session_id, {"created_at": now_iso, "updated_at": now_iso})
        
        return SessionHistoryResponse(
            session_id=session_id,
            messages=messages,
            created_at=meta["created_at"],
            updated_at=meta["updated_at"]
        )

    def append_turn(self, session_id: str, user_question: str, assistant_answer: str, response_data: Optional[Dict[str, Any]] = None):
        now_iso = datetime.now(timezone.utc).isoformat()
        if session_id not in self._store:
            self._store[session_id] = []
            self._metadata[session_id] = {"created_at": now_iso, "updated_at": now_iso}
        
        self._store[session_id].append(
            SessionMessage(
                role="user",
                content=user_question,
                timestamp=now_iso
            )
        )
        self._store[session_id].append(
            SessionMessage(
                role="assistant",
                content=assistant_answer,
                timestamp=now_iso,
                response_data=response_data
            )
        )
        self._metadata[session_id]["updated_at"] = now_iso

    def clear(self, session_id: str):
        if session_id in self._store:
            del self._store[session_id]
        if session_id in self._metadata:
            del self._metadata[session_id]

session_store = SessionStore()
