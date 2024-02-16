from __future__ import annotations

import numpy as np
import seaborn as sns
from astropy.timeseries import LombScargle
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
                fraction_times.append(point.JD)
                brightnesses.append(point.brightness)

        points = zip(fraction_times, brightnesses)
        points = sorted(points, key=lambda point: point[0])

        _, ax = plt.subplots(figsize=(15, 10))
        ax.scatter(*zip(*points))
        ax.set_xlabel("Date")
        ax.set_ylabel("Brightness")
        ax.set_title(f"Lightcurve of {self.name}")

        plt.show()

    def plot_lightcurves(
        self,
        start_ind: int | None = None,
        end_ind: int | None = None,
        save: bool = False,
    ) -> None:
        """
        Plot all the lightcurves of the asteroid.

        :param start_ind: The index of the first lightcurve to plot (inclusive).
        :param end_ind: The index of the last lightcurve to plot (exclusive).
        :param save: If True, save the plot in a file.
        """
        if start_ind is None:
            start_ind = 0
        if end_ind is None:
            end_ind = len(self.lightcurves)

        brightnesses = []
        times = []

        for lc in self.lightcurves[start_ind:end_ind]:
            for point in lc.points:
                times.append(point.JD)
                brightnesses.append(point.brightness)

        times = np.array(times)
        brightnesses = np.array(brightnesses)

        ls = LombScargle(times, brightnesses)
        frequency, power = ls.autopower()
        best_frequency = frequency[np.argmax(power)]
        best_period = 1 / best_frequency

        print(f"Best period: {best_period}")

        phases = ((times - times.min()) % best_period) / best_period

        sorted_indices = np.argsort(phases)
        sorted_phases = phases[sorted_indices]
        sorted_brightnesses = brightnesses[sorted_indices]

        # Leave only thos points that have phase between (inclusive) 0.2 and 0.7
        mask = (0.2 <= sorted_phases) & (sorted_phases <= 0.7)
        sorted_phases = sorted_phases[mask]
        sorted_brightnesses = sorted_brightnesses[mask]

        _, ax = plt.subplots(figsize=(15, 10))
        ax.scatter(sorted_phases, sorted_brightnesses)
        ax.set_xlabel("Phase")
        ax.set_ylabel("Brightness")
        ax.set_title(f"Lightcurve of {self.name}")

        t_fit = np.linspace(0, 1)
        y_fit = ls.model(t_fit, best_frequency)
        ax.plot(t_fit, y_fit, "r")

        # Set x-limit to 0-1 (slighltly less / more to see the points)
        ax.set_xlim(-0.05, 1.05)

        if save:
            plt.savefig(f"../plots/{self.name}.png")
        else:
            plt.show()

        return phases, brightnesses

    def __repr__(self) -> str:
        return f"Asteroid(id={self.id}, name={self.name}, period={self.period}, lightcurves={len(self.lightcurves)})"
