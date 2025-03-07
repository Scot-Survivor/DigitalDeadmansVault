from fastapi import Depends
from typing import Annotated
from sqlmodel import Session
from .models import get_session
from .middlewares.auth import HMACAuth

SessionDepends = Depends(get_session)
HMACAuthDepends = Depends(HMACAuth())
