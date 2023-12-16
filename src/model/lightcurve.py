from datetime import datetime

from pydantic import BaseModel, Field, validator

from src.model.point import Point


class LightCurve(BaseModel):
    """
    A light curve is a series of measurements of the brightness of an object
    over time.
    """

    id: int
    scale: int
    points: list[Point]
    created_at: datetime = Field(..., alias="created")
    updated_at: datetime = Field(..., alias="modified")
    points_count: int

    @validator("points", pre=True)
    def parse_points(cls, points):
        """
        Parse points from a string into a list of lists of floats.
        """
        return [Point.from_list(row.split()) for row in points.split("\n") if row]
