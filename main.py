from fastapi import FastAPI
from api.v1.endpoints import leads

app = FastAPI()

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
