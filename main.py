from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import leads
from db.sql import init_db
from utils.exceptions import BaseAppException
from utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("server is starting")
    await init_db()
    yield
    logger.critical("server is shutting down")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BaseAppException)
async def app_exception_handler(request, exc):
    import traceback
    logger.exception(f"Application error traceback starts ==>")
    logger.error(traceback.format_exc())
    logger.exception(f"Application error traceback ends\n")
    logger.exception(f"Application error msg ==> {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )    

# Include routers
app.include_router(
    leads.router, 
    prefix="/api/v1/leads", 
    tags=["leads"]
)

@app.get("/")
async def root():
    return [{
        'name': 'Test One'
    }]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
