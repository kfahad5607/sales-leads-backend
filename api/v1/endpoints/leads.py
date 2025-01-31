from fastapi import APIRouter


router = APIRouter()

@router.get("/")
async def get_leads():
    return list(['Lead 1', 'Lead 2'])