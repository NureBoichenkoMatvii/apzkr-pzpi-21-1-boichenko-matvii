import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import settings
from database import db
from database import models
from extensions.babel import babel
from logger import configure_logger
from services.mqtt.mqtt_service import mqtt_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.connect()

    async with db.async_engine.connect() as conn:
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DATABASE_SCHEMA}"))
        await conn.run_sync(models.DbBaseModel.metadata.create_all)
        await conn.commit()

    db.init_load_medecines()

    mqtt_service.connect()

    yield

    mqtt_service.disconnect()
    await db.disconnect()


def create_app():
    app = FastAPI(lifespan=lifespan)

    @app.exception_handler(Exception)
    def main_error_handler(request: Request, exc: Exception):
        return JSONResponse({"success": False, "error": exc.__class__.__name__, "message": str(exc)},
                            status_code=500)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    babel.init_app(app)

    logging.basicConfig(
        level="DEBUG",
        format="%(asctime)s %(name)s %(module)s %(funcName)s %(levelname)s %(message)s"
    )
    configure_logger(logger_name="app_main", log_level="DEBUG")

    from api.router import api

    app.include_router(api)

    from extensions.admin.main import init_admin
    init_admin(app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    # print(os.environ)
    uvicorn.run(app="main:create_app", factory=True,
                host="127.0.0.1", port=8001, reload=settings.DEBUG)
    #workers=settings.WEB_CONCURRENCY)
