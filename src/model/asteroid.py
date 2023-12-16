from pydantic import BaseModel

from src.model.lightcurve import LightCurve


class Asteroid(BaseModel):
    id: int
    name: str
    lightcurves: list[LightCurve]
