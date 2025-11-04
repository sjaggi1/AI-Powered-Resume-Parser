from fastapi import APIRouter

router = APIRouter()

@router.get("/analytics")
def test_analytics():
    return {"message": "Analytics route working!"}
