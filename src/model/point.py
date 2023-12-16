from __future__ import annotations

import warnings
from datetime import datetime

from astropy.time import Time
from pydantic import BaseModel, ValidationError, validator

warnings.filterwarnings("ignore", module="erfa")  # Ignore warnings from erfa UTC


class Point(BaseModel):
    time: datetime
    brightness: float  # In intensity units

    # asteroid-centric cartesian coordinates
    x_sun: float
    y_sun: float
    z_sun: float
    x_earth: float
    y_earth: float
    z_earth: float

    @validator("time", pre=True)
    def parse_time(cls, jd):
        """
        Convert time from JD to datetime.
        """
        return Time(jd, format="jd").datetime

    @validator("time")
    def validate_time(cls, time):
        """
        Validate time is between 1900 and 2023.
        """
        if time.year < 1900 or time.year > 2023:
            raise ValidationError("Time must be between 1900 and 2023")

        return time

    @staticmethod
    def from_list(data: list) -> Point:
        """
        Create a Point object from a list of data.

        :param data: The list of data.

        :return: A Point object.
        """
        return Point(**dict(zip(Point.model_fields.keys(), data)))
