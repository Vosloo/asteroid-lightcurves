from __future__ import annotations

from datetime import datetime
from functools import cached_property
from typing import Self

import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.config import ConfigDict

from astrofit.model.point import Point


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
            f"Lightcurve(id={self.id}, period={self.get_period(in_hours=True):.5f}h, "
            f"points_count={self.points_count}, first_JD={self.first_JD}, last_JD={self.last_JD})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __len__(self) -> int:
        return self.points_count

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

    @field_validator("points", mode="after")
    @classmethod
    def sort_points(cls, points: list[Point]) -> list[Point]:
        """
        Sort points by Julian Date.
        """
        return sorted(points, key=lambda p: p.JD)

    @model_validator(mode="after")
    def check_points_count(self) -> Self:
        """
        Check that the number of points is equal to the points_count.
        """
        if len(self.points) != self.points_count:
            raise ValueError("Number of points does not match points_count")

        return self

    @model_validator(mode="after")
    def ensure_positive_period(self) -> Self:
        assert not self.get_period(in_hours=True) < 0, "Invalid period of light curve!"

        return self

    @staticmethod
    def from_points(og_lightcurve: Lightcurve, points: list[Point]) -> Lightcurve:
        return Lightcurve(
            id=og_lightcurve.id,
            scale=og_lightcurve.scale,
            points=points,
            created=og_lightcurve.created_at,
            modified=og_lightcurve.updated_at,
            points_count=len(points),
        )

    def get_period(self, in_hours: bool = False) -> float:
        """
        Get the period of the light curve converted to hours if less than 1 day.
        """
        diff = self.last_JD - self.first_JD

        return diff * 24 if in_hours else diff

    def merge(self, other: Lightcurve) -> Lightcurve:
        """
        Merge two light curves.
        """
        sorted_points = sorted(self.points + other.points, key=lambda p: p.JD)

        return Lightcurve.from_points(self, sorted_points)

    def plot(self, color: tuple | None = None, ax: Axes | None = None, asteroid_name: str = ""):
        """
        Plot the light curve.
        """
        if color is None:
            color = sns.color_palette("icefire")[0]

        diff = self.last_JD - self.first_JD
        if diff < 1:
            _range = f"{diff * 24:.4f} hours"
        else:
            _range = f"{diff:.4f} days"

        if ax is None:
            plt.scatter(self.time_arr, self.brightness_arr, color=color, s=5)
            plt.xlabel("JD")
            plt.ylabel("Brightness")

            prefix = asteroid_name
            if prefix:
                prefix += " - "

            plt.title(f"{prefix}Lightcurve id={self.id} - range={_range}")
        else:
            ax.scatter(self.time_arr, self.brightness_arr, color=color, s=5)

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

    @cached_property
    def time_arr(self) -> list[float]:
        """
        Get the time of the light curve.
        """
        return [point.JD for point in self.points]

    @cached_property
    def brightness_arr(self) -> list[float]:
        """
        Get the brightness of the light curve.
        """
        return [point.brightness for point in self.points]

    @cached_property
    def period(self) -> float:
        """
        Get the period of the light curve.
        """
        return self.get_period(in_hours=True)
