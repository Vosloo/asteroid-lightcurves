from datetime import datetime

from matplotlib import pyplot as plt
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict

from src.model.point import Point


class Lightcurve(BaseModel):
    """
    A light curve is a series of measurements of the brightness of an object
    over time.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: int
    scale: int
    points: list[Point]
    created_at: datetime = Field(alias="created")
    updated_at: datetime = Field(alias="modified")
    points_count: int

    def __repr__(self) -> str:
        return f"Lightcurve(id={self.id}, created_at={self.created_at} scale={self.scale}, points_count={self.points_count})"

    def __str__(self) -> str:
        return self.__repr__()

    @field_validator("points", mode="before")
    @classmethod
    def parse_points(cls, points):
        """
        Parse points from a string into a list of lists of floats.
        """
        return [Point.from_list(row.split()) for row in points.split("\n") if row]

    @property
    def first_JD(self) -> float:
        """
        Get the start Julian Date of the light curve.
        """
        return self.points[0].JD

    @property
    def last_JD(self) -> float:
        """
        Get the end Julian Date of the light curve.
        """
        return self.points[-1].JD

    def plot(self):
        """
        Plot the light curve.
        """
        brightnesses = []
        times = []

        for point in self.points:
            times.append(point.JD)
            brightnesses.append(point.brightness)

        _, ax = plt.subplots(figsize=(15, 10))
        ax.scatter(times, brightnesses)
        ax.set_xlabel("JD")
        ax.set_ylabel("Brightness")
        ax.set_title(f"Lightcurve (id: {self.id})")
