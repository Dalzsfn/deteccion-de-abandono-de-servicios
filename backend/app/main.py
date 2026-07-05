from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import clientes_riesgo_routes, clientes_routes, telegram_routes
from backend.app.services import telegram_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    await telegram_service.startup()
    yield
    await telegram_service.shutdown()


app = FastAPI(title="API de Retención de Gimnasio", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes_riesgo_routes.router, prefix="/api/ml",       tags=["Predicciones"])
app.include_router(clientes_routes.router,        prefix="/api/clientes", tags=["Base de Datos"])
app.include_router(telegram_routes.router,        prefix="/api/telegram", tags=["Telegram"])


@app.get("/")
def health_check():
    return {"estado": "Servidor corriendo perfectamente"}
