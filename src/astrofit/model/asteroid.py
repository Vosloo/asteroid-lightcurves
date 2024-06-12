from __future__ import annotations

from functools import cached_property

import seaborn as sns
from pydantic import BaseModel, field_validator

from astrofit.model.enums import EnumSortOption
from astrofit.model.lightcurve import Lightcurve

sns.set_theme()


LIGHTCURVE_KEY = "LightCurve"
ASTEROID_ID_KEY = "asteroid_id"


class Asteroid(BaseModel):
    id: int
    name: str
    period: float
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
    def from_lightcurves(id: int, name: str, period: float, data: list[dict]) -> Asteroid:
        """
        Create an Asteroid object from a list of lightcurves data (list of JSON).

        :param name: The name of the asteroid.
        :param period: The period of the asteroid.
        :param data: The list of lightcurves data.
        :param asteroid_id: The id of the asteroid. If None, the id will be extracted from the first lightcurve.

        :return: An Asteroid object.
        """
        lightcurves = [Lightcurve(**lc[LIGHTCURVE_KEY]) for lc in data]
        return Asteroid(id=id, name=name, period=period, lightcurves=lightcurves)

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

    def get_lightcurves(self, by: EnumSortOption = EnumSortOption.PERIOD) -> list[Lightcurve]:
        """
        Get the lightcurves of the asteroid.

        :return: The lightcurves.
        """
        if by == EnumSortOption.PERIOD:
            return sorted(self.lightcurves, key=lambda lc: lc.get_period(), reverse=True)
        elif by == EnumSortOption.POINTS:
            return sorted(self.lightcurves, key=lambda lc: lc.points_count, reverse=True)
        else:
            options = ["EnumSortOptions." + option.name for option in EnumSortOption]
            raise ValueError(f"Invalid 'by' value: {by}, use: {options}")

    def get_longest_lightcurve(self, by: EnumSortOption = EnumSortOption.PERIOD) -> Lightcurve:
        """
        Get the longest lightcurve of the asteroid.

        :return: The longest lightcurve.
        """
        if by == EnumSortOption.PERIOD:
            return max(self.lightcurves, key=lambda lc: lc.get_period())
        elif by == EnumSortOption.POINTS:
            return max(self.lightcurves, key=lambda lc: lc.points_count)
        else:
            options = ["EnumSortOptions." + option.name for option in EnumSortOption]
            raise ValueError(f"Invalid 'by' value: {by}, use: {options}")

    @cached_property
    def map_id_lightcurves(self) -> dict[int, Lightcurve]:
        """
        Get a map of lightcurves by id.

        :return: A map of lightcurves by id.
        """
        return {lc.id: lc for lc in self.lightcurves}

    def __repr__(self) -> str:
        return f"Asteroid(id={self.id}, name={self.name}, period={self.period}, lightcurves={len(self.lightcurves)})"
