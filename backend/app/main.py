import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

db_menu = {}


class MenuCreateSchema(BaseModel):
    nama: str = Field(..., min_length=1)
    sku: str = Field(..., pattern=r"^KOPI-\d{3}$")
    kategori: str = Field(..., pattern=r"^(kopi|non-kopi|makanan)$")
    harga: int = Field(..., gt=0)


class MenuResponseSchema(MenuCreateSchema):
    id: str


@app.post(
    "/api/menu",
    response_model=MenuResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_menu(payload: MenuCreateSchema, response: Response):
    menu_id = str(uuid.uuid4())
    data_menu = payload.model_dump()
    data_menu["id"] = menu_id

    db_menu[menu_id] = data_menu
    response.headers["Location"] = f"/api/menu/{menu_id}"
    return data_menu


@app.get("/api/menu", response_model=List[MenuResponseSchema])
def get_all_menu(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: Optional[str] = None,
):
    results = list(db_menu.values())
    if search:
        search_lower = search.lower()
        results = [
            m
            for m in results
            if search_lower in m["nama"].lower()
            or search_lower in m["sku"].lower()
        ]
    return results[skip : skip + limit]


@app.get("/api/menu/{id}", response_model=MenuResponseSchema)
def get_menu_by_id(id: str):
    if id not in db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu tidak ditemukan"
        )
    return db_menu[id]