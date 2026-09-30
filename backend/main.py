import re
from typing import List, Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field, field_validator
@app.get("/health")
def health_check():
    return {"status": "ok"}

app = FastAPI(title="WAD 2026 Individu API")

# Database sementara (In-Memory)
db_menu = {}


# --- SCHEMAS ---
# Skema Input (tanpa id)
class MenuCreate(BaseModel):
    nama: str
    sku: str = Field(..., description="Format: KOPI-000")
    kategori: str = Field(..., description="Pilihan: kopi / non-kopi / makanan")
    harga: float = Field(..., gt=0)

    @field_validator("sku")
    def validate_sku(cls, v):
        pattern = r"^KOPI-\d{3}$"
        if not re.match(pattern, v):
            raise ValueError("SKU harus berformat KOPI-000 (contoh: KOPI-001)")
        return v

    @field_validator("kategori")
    def validate_kategori(cls, v):
        allowed = ["kopi", "non-kopi", "makanan"]
        if v.lower() not in allowed:
            raise ValueError(
                f"Kategori harus salah satu dari: {', '.join(allowed)}"
            )
        return v.lower()


# Skema Output (mengandung id yang dibuat oleh server)
class MenuResponse(MenuCreate):
    id: str


# --- ENDPOINTS ---


# 1. POST /api/menu (Status 201 Created + Header Location)
@app.post(
    "/api/menu", response_model=MenuResponse, status_code=status.HTTP_201_CREATED
)
def create_menu(item: MenuCreate, response: Response):
    new_id = str(uuid4())
    created_item = MenuResponse(id=new_id, **item.model_dump())
    db_menu[new_id] = created_item

    # Menambahkan Header Location sesuai spesifikasi
    response.headers["Location"] = f"/api/menu/{new_id}"
    return created_item


# 2. GET /api/menu (Dukung ?skip, ?limit, ?search)
@app.get("/api/menu", response_model=List[MenuResponse])
def get_all_menu(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
):
    items = list(db_menu.values())

    if search:
        items = [
            item
            for item in items
            if search.lower() in item.nama.lower()
            or search.lower() in item.sku.lower()
        ]

    return items[skip : skip + limit]


# 3. GET /api/menu/{id} (Status 404 jika ID tidak ada)
@app.get("/api/menu/{id}", response_model=MenuResponse)
def get_menu_by_id(id: str):
    if id not in db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu tidak ditemukan"
        )
    return db_menu[id]
@app.get("/health")
def health_check():
    return {"status": "ok"}