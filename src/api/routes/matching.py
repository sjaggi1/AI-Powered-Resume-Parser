from fastapi import APIRouter

router = APIRouter()

@router.get("/matching")
def test_matching():
    return {"message": "Matching route working!"}
