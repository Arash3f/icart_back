import os
import time

from src.create_app import create_fastapi_app
from src.database.init_db import init_db
from src.database.session import SessionLocal

# ---------------------------------------------------------------------------
app = create_fastapi_app()

# ---------------------------------------------------------------------------
if os.environ.get("APP_ENV") == "Development":

    @app.middleware("http")
    async def add_process_time_header(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(f"{process_time:0.4f} sec")
        return response


# ---------------------------------------------------------------------------
@app.on_event("startup")
async def initial_data():
    async with SessionLocal() as session:
        await init_db(db=session)


# ---------------------------------------------------------------------------
@app.get("/")
def index():
    return {"Status": 200, "Message": "I'm still working!"}
