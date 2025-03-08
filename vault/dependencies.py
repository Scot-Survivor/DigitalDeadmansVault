from fastapi import Depends
from vault.models import get_session
from vault.middlewares.auth import HMACAuth

SessionDepends = Depends(get_session)
HMACAuthDepends = Depends(HMACAuth())
