from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from app.data import SESSIONS_DB
from app.schemas import SessionCreate, SessionResponse, PaginatedSessionResponse

app = FastAPI(title="WAD Session API")

# Setup CORS untuk origin Frontend (Vite default: http://localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper untuk auto-increment ID
def get_next_id():
    return max([s["id"] for s in SESSIONS_DB], default=0) + 1


@app.get("/sessions", response_model=PaginatedSessionResponse)
def get_sessions(
    q: str | None = Query(None, description="Search by title or speaker"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50)
):
    filtered = SESSIONS_DB
    
    # Fitur Search
    if q:
        search_lower = q.lower()
        filtered = [
            s for s in filtered
            if search_lower in s["title"].lower() or search_lower in s["speaker"].lower()
        ]
    
    # Fitur Pagination
    total = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_data = filtered[start_idx:end_idx]

    return {
        "data": paginated_data,
        "total": total,
        "page": page,
        "limit": limit
    }


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session_by_id(session_id: int):
    session = next((s for s in SESSIONS_DB if s["id"] == session_id), None)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session dengan ID {session_id} tidak ditemukan"
        )
    return session


@app.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate):
    new_session = payload.model_dump()
    new_session["id"] = get_next_id()
    SESSIONS_DB.append(new_session)
    return new_session


@app.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int):
    global SESSIONS_DB
    session = next((s for s in SESSIONS_DB if s["id"] == session_id), None)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session dengan ID {session_id} tidak ditemukan"
        )
    SESSIONS_DB = [s for s in SESSIONS_DB if s["id"] != session_id]
    return None