from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints import leads
from utils.exceptions import BaseAppException
from utils.logger import logger
from config import settings

app = FastAPI(title=settings.APP_NAME, debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
