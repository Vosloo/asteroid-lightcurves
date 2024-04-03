from __future__ import annotations

from datetime import datetime
from typing import Self

from matplotlib import pyplot as plt
from pydantic import BaseModel, Field, field_validator, model_validator
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
        return (
            f"Lightcurve(id={self.id}, period={self.get_period(in_hours=True):.5f}h "
            f"scale={self.scale}, points_count={self.points_count})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    @field_validator("points", mode="before")
    @classmethod
    def parse_points(cls, points):
        """
        Parse points from a string into a list of lists of floats.
        """
        if isinstance(points, str):
            return [Point.from_list(row.split()) for row in points.split("\n") if row]
        else:
            return points

    @model_validator(mode="after")
    def check_points_count(self) -> Self:
        """
        Check that the number of points is equal to the points_count.
        """
        if len(self.points) != self.points_count:
            raise ValueError("Number of points does not match points_count")

        return self

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

    def get_period(self, in_hours: bool = False) -> float:
        """
        Get the period of the light curve converted to hours if less than 1 day.
        """
        diff = self.last_JD - self.first_JD

        return diff * 24 if in_hours else diff

    def plot(self, ax=None):
        """
        Plot the light curve.
        """
        brightnesses = []
        times = []

        for point in self.points:
            times.append(point.JD)
            brightnesses.append(point.brightness)

        if ax is not None:
            ax.scatter(times, brightnesses)
            ax.set_xlabel("JD")
            ax.set_ylabel("Brightness")
            ax.set_title(f"Lightcurve id={self.id} period={self.get_period(True):.5f}h")
        else:
            plt.scatter(times, brightnesses)
            plt.xlabel("JD")
            plt.ylabel("Brightness")
            plt.title(f"Lightcurve id={self.id} period={self.get_period(True):.5f}h")
