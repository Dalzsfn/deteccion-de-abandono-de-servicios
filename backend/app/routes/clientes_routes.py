from fastapi import APIRouter, HTTPException
from app.services import ml_service
from backend.database.queries import get_clientes

router = APIRouter()

@router.get("/clientes")
def read_clientes():
    return get_clientes()