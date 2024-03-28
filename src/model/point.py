from __future__ import annotations

from pydantic import BaseModel


class Point(BaseModel):
    JD: float
    brightness: float  # In intensity units

    # asteroid-centric cartesian coordinates
    x_sun: float
    y_sun: float
    z_sun: float
    x_earth: float
    y_earth: float
    z_earth: float

    @staticmethod
    def from_list(data: list) -> Point:
        """
        Create a Point object from a list of data.

        :param data: The list of data.

        :return: A Point object.
        """
        return Point(**dict(zip(Point.model_fields.keys(), data)))
