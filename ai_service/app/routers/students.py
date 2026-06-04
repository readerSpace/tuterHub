from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud
from ..database import get_db
from ..schemas import StudentSummary


router = APIRouter()


@router.get('/students', response_model=list[StudentSummary])
def get_students(db: Session = Depends(get_db)):
    return crud.list_students(db)
