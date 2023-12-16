from datetime import datetime

from pydantic import BaseModel, Field, validator


class LightCurve(BaseModel):
    """
    A light curve is a series of measurements of the brightness of an object
    over time.
    """

    id: int
    scale: int
    points: list[list[float]]
    created_at: datetime = Field(..., alias="created")
    updated_at: datetime = Field(..., alias="modified")
    points_count: int

    @validator("points", pre=True)
    def parse_points(cls, v):
        """
        Parse points from a string into a list of lists of floats.
        """
        return [list(map(float, i.split())) for i in v.split("\n") if i]
