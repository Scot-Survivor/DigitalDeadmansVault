from typing import AnyStr
from pydantic import BaseModel
from ..enums.auth import HMACAlgorithm


class HMACObject(BaseModel):
    key: AnyStr
    message: AnyStr
    algorithm: HMACAlgorithm


    @property
    def signature(self) -> AnyStr:
        return self.algorithm.hash(self.message)
