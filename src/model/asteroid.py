from __future__ import annotations

import seaborn as sns
from matplotlib import pyplot as plt
from pydantic import BaseModel

from src.model.lightcurve import LightCurve

sns.set_theme()


LIGHTCURVE_KEY = "LightCurve"
ASTEROID_ID_KEY = "asteroid_id"


class Asteroid(BaseModel):
    id: int
    name: str
    period: float
    lightcurves: list[LightCurve]

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
        lightcurves = [LightCurve(**lc[LIGHTCURVE_KEY]) for lc in data]
        return Asteroid(id=id, name=name, period=period, lightcurves=lightcurves)

    def plot_lc_by_dates(self, s_n: int | None = None, e_n: int | None = None) -> None:
        if s_n is None:
            s_n = 0
        if e_n is None:
            e_n = len(self.lightcurves)

        lcs = self.lightcurves[s_n:e_n]
        fraction_times = []
        brightnesses = []
        for lc in lcs:
            for point in lc.points:
                fraction_times.append(
                    point.time.day + point.time.hour / 24 + point.time.minute / 1440 + point.time.second / 86400
                )
                brightnesses.append(point.brightness)

        points = zip(fraction_times, brightnesses)
        points = sorted(points, key=lambda point: point[0])

        _, ax = plt.subplots(figsize=(15, 10))
        ax.scatter(*zip(*points))
        ax.set_xlabel("Date")
        ax.set_ylabel("Brightness")
        ax.set_title(f"Lightcurve of {self.name}")

        plt.show()

    def plot_lightcurves(self, s_n: int | None = None, e_n: int | None = None, save: bool = False) -> None:
        """
        Plot all the lightcurves of the asteroid.

        :param save: If True, save the plot in a file.
        """
        if s_n is None:
            s_n = 0
        if e_n is None:
            e_n = len(self.lightcurves)

        rotation = 24 / self.period

        fraction_times = []
        brightnesses = []
        for lc in self.lightcurves[s_n:e_n]:
            for point in lc.points:
                fraction_times.append(
                    point.time.day + point.time.hour / 24 + point.time.minute / 1440 + point.time.second / 86400
                )
                brightnesses.append(point.brightness)

        phases = []
        for time in fraction_times:
            phases.append(time / rotation % 1)

        points = zip(phases, brightnesses)
        points = sorted(points, key=lambda point: point[0])

        _, ax = plt.subplots(figsize=(15, 10))
        ax.scatter(*zip(*points))
        ax.set_xlabel("Phase")
        ax.set_ylabel("Brightness")
        ax.set_title(f"Lightcurve of {self.name}")

        # Set x-limit to 0-1 (slighltly less / more to see the points)
        ax.set_xlim(-0.05, 1.05)

        if save:
            plt.savefig(f"../plots/{self.name}.png")
        else:
            plt.show()

        return phases, brightnesses

    def __repr__(self) -> str:
        return f"Asteroid(id={self.id}, name={self.name}, period={self.period}, lightcurves={len(self.lightcurves)})"
