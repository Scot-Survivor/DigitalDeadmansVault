from typing import Annotated
from fastapi import APIRouter
from ..dependencies import HMACAuthDepends

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.get("/protected", dependencies=[HMACAuthDepends])
def protected(access_key: Annotated[str, HMACAuthDepends]):
    return {"message": "This is a protected endpoint", "access_key": access_key}
