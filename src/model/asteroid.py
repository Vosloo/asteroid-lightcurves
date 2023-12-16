from __future__ import annotations

from pydantic import BaseModel

from src.model.lightcurve import LightCurve


LIGHTCURVE_KEY = "LightCurve"
ASTEROID_ID_KEY = "asteroid_id"


class Asteroid(BaseModel):
    id: int
    name: str
    lightcurves: list[LightCurve]

    @staticmethod
    def from_lightcurves(id: int, name: str, data: list[dict]) -> Asteroid:
        """
        Create an Asteroid object from a list of lightcurves data (list of JSON).

        :param name: The name of the asteroid.
        :param data: The list of lightcurves data.
        :param asteroid_id: The id of the asteroid. If None, the id will be extracted from the first lightcurve.

        :return: An Asteroid object.
        """
        lightcurves = [LightCurve(**lc[LIGHTCURVE_KEY]) for lc in data]
        return Asteroid(id=id, name=name, lightcurves=lightcurves)

    def __repr__(self) -> str:
        return f"Asteroid(id={self.id}, name={self.name}, lightcurves={len(self.lightcurves)})"
