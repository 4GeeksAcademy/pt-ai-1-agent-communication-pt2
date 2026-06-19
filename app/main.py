from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers.api_v1 import router as api_v1_router
from app.routers.api_v2 import router as api_v2_router
from app.web.admin import router as admin_router
from app.web.auth import router as auth_router
from app.web.student import router as student_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Fictionary API",
    description="A REST API for students learning HTTP and API interaction.",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.include_router(api_v1_router)
app.include_router(api_v2_router)
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(admin_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="home.html", context={})
