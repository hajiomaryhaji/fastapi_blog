from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.AUTO_CREATE_TABLES:
        if settings.DATABASE_URL.startswith("sqlite"):
            Path("database").mkdir(parents=True, exist_ok=True)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Root
@app.get("/", include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse(request, "welcome.html", {"message": "FastAPI is Awesome."})

# Health
@app.get("/health")
async def health():
    return {"message": "Server is running"}


# General exception handler
@app.exception_handler(HTTPException)
async def general_http_exception_handler(request: Request, exception: HTTPException):
    message = (
        exception.detail if exception.detail else "An error occured. Please check your request and try again"
    )

    if request.url.path.startswith(settings.API_V1_PREFIX):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message
        },
        exception.status_code,
    )


# Request validation exception handler
@app.exception_handler(RequestValidationError)
async def request_alidation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith(settings.API_V1_PREFIX):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": jsonable_encoder(exception.errors())}
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request. Please check your input and try again."
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

