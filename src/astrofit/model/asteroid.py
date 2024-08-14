from __future__ import annotations

from functools import cached_property

import seaborn as sns
from pydantic import BaseModel, ValidationError, field_validator

from astrofit.model.enums import SortOptionEnum
from astrofit.model.lightcurve import Lightcurve

sns.set_theme()


LIGHTCURVE_KEY = "LightCurve"
ASTEROID_ID_KEY = "asteroid_id"


class Asteroid(BaseModel):
    id: int
    name: str
    period: float
    lambd: float
    beta: float
    lightcurves: list[Lightcurve]

    @field_validator("lightcurves")
    @classmethod
    def sort_lightcurves(cls, v: list[Lightcurve]) -> list[Lightcurve]:
        # Pre-sort lightcurves by first_JD
        lightcurves = sorted(v, key=lambda lc: lc.first_JD)

        # Merge lightcurves that overlap
        sorted_lightcurves = []
        curr_ind = 0
        curr_lc = lightcurves[curr_ind]
        while True:
            if curr_ind >= len(lightcurves) - 1:
                break

            next_lc = lightcurves[curr_ind + 1]

            if curr_lc.last_JD >= next_lc.first_JD:
                curr_lc = curr_lc.merge(next_lc)
            else:
                sorted_lightcurves.append(curr_lc)
                curr_lc = next_lc

            curr_ind += 1

        sorted_lightcurves.append(curr_lc)

        return sorted_lightcurves

    @staticmethod
    def from_lightcurves(id: int, name: str, period: float, lambd: float, beta: float, data: list[dict]) -> Asteroid:
        """
        Create an Asteroid object from a list of lightcurves data (list of JSON).

        :param name: The name of the asteroid.
        :param period: The period of the asteroid.
        :param data: The list of lightcurves data.
        :param asteroid_id: The id of the asteroid. If None, the id will be extracted from the first lightcurve.

        :return: An Asteroid object.
        """
        try:
            lightcurves = [Lightcurve(**lc) for lc in data]
            return Asteroid(id=id, name=name, period=period, lambd=lambd, beta=beta, lightcurves=lightcurves)
        except ValidationError as e:
            print(f"Error creating Asteroid {name}!")
            raise e

    def get_lightcurve(self, id: int) -> Lightcurve:
        """
        Get a lightcurve by id.

        :param id: The id of the lightcurve.

        :return: The lightcurve.
        """
        res = self.map_id_lightcurves.get(id)
        if res is None:
            raise ValueError(f"Lightcurve with id {id} not found")

        return res

    def get_lightcurves(self, by: SortOptionEnum = SortOptionEnum.PERIOD) -> list[Lightcurve]:
        """
        Get the lightcurves of the asteroid.

        :return: The lightcurves.
        """
        if by == SortOptionEnum.PERIOD:
            return sorted(self.lightcurves, key=lambda lc: lc.get_period(), reverse=True)
        elif by == SortOptionEnum.POINTS:
            return sorted(self.lightcurves, key=lambda lc: lc.points_count, reverse=True)
        else:
            options = ["EnumSortOptions." + option.name for option in SortOptionEnum]
            raise ValueError(f"Invalid 'by' value: {by}, use: {options}")

    def get_longest_lightcurve(self, by: SortOptionEnum = SortOptionEnum.PERIOD) -> Lightcurve:
        """
        Get the longest lightcurve of the asteroid.

        :return: The longest lightcurve.
        """
        if by == SortOptionEnum.PERIOD:
            return max(self.lightcurves, key=lambda lc: lc.get_period())
        elif by == SortOptionEnum.POINTS:
            return max(self.lightcurves, key=lambda lc: lc.points_count)
        else:
            options = ["EnumSortOptions." + option.name for option in SortOptionEnum]
            raise ValueError(f"Invalid 'by' value: {by}, use: {options}")

    @cached_property
    def map_id_lightcurves(self) -> dict[int, Lightcurve]:
        """
        Get a map of lightcurves by id.

        :return: A map of lightcurves by id.
        """
        return {lc.id: lc for lc in self.lightcurves}

    def __repr__(self) -> str:
        return (
            f"Asteroid(id={self.id}, name={self.name}, period={self.period}, "
            f"lambda={self.lambd}, beta={self.beta}, lightcurves={len(self.lightcurves)})"
        )
