import math

import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from astrofit.model import Lightcurve, LightcurveBin

plt.rcParams["figure.figsize"] = (12, 6)
sns.set_theme()


MAX_COLS = 4


class LightcurvePlotter:
    def plot_lightcurve(self, lightcurve: Lightcurve):
        """
        Plot the light curve.

        :param lightcurve: The light curve to plot.
        """
        lightcurve.plot(color=sns.color_palette("icefire")[0])
        plt.show()

    def plot_bins_on_grid(self, bins: list[LightcurveBin], grid_size: tuple[int, int] | None = None):
        """
        Plot the light curve bins on a grid.

        :param grid_size: The size of the grid.
        :param bins: The light curve bins to plot.
        """
        if not bins:
            raise ValueError("No bins to plot!")

        if grid_size is None:
            grid_size = self._get_grid_size(bins)

        elif grid_size[0] * grid_size[1] != len(bins):
            raise ValueError("Grid size does not match the number of bins!")

        fig, axs = plt.subplots(grid_size[0], grid_size[1], figsize=(14, 8))

        for i, _bin in enumerate(bins):
            ax = axs[i // grid_size[1], i % grid_size[1]]
            ax.set_xlabel("Julian Date")
            ax.set_ylabel("Brightness")
            ax.set_title(f"{repr(_bin)}")
            self.plot_lightcurves(_bin, split_plots=False, ax=ax)

        plt.tight_layout()
        plt.show()

    def plot_lightcurves(
        self,
        lightcurves: list[Lightcurve] | LightcurveBin,
        split_plots: bool = False,
        ax: Axes | None = None,
        asteroid_name: str = "",
    ):
        """
        Plot the light curves.

        :param lightcurves: The light curves to plot.
        :param subplots: Whether to plot the light curves in subplots.
        """
        colors = sns.color_palette("icefire", len(lightcurves))

        min_JD = None
        max_JD = None
        for i, lc in enumerate(lightcurves):
            if min_JD is None or lc.first_JD < min_JD:
                min_JD = lc.first_JD
            if max_JD is None or lc.last_JD > max_JD:
                max_JD = lc.last_JD

            if split_plots:
                lc.plot(color=colors[i], asteroid_name=asteroid_name)
                plt.show()
            elif ax is not None:
                lc.plot(color=colors[i], ax=ax, asteroid_name=asteroid_name)
            else:
                lc.plot(color=colors[i], asteroid_name=asteroid_name)

        if min_JD is None or max_JD is None:
            raise ValueError("No light curves to plot!")

        if split_plots or ax is not None:
            return

        diff = max_JD - min_JD
        if diff < 1:
            _range = f"{diff * 24:.4f} hours"
        else:
            _range = f"{diff:.4f} days"

        plt.xlabel("Julian Date")
        plt.ylabel("Brightness")

        prefix = asteroid_name
        if prefix:
            prefix += " - "

        plt.title(f"{prefix}{len(lightcurves)} lightcurves - range={_range}")

        plt.show()

    def plot_phased_lightcurves(
        self,
        lightcurves: list[Lightcurve] | LightcurveBin,
        period: float,
        known_period: float | None = None,
    ):
        ref_JD = None
        for lc in lightcurves:
            if ref_JD is None:
                ref_JD = lc.first_JD

            phases = []
            brightness = []
            for point in lc.points:

                phase = self._get_phase(point.JD, ref_JD, period)

                phases.append(phase)
                brightness.append(point.brightness)

            plt.scatter(phases, brightness, s=8, label=f"Lightcurve {lc.id}")

        diff_known = ""
        if known_period is not None:
            diff_known = f" ~ diff from known: {abs(known_period - period):.5f}"

        plt.title(f"Phased {len(lightcurves)} lightcurves (period: {period:.5f}h{diff_known})")
        plt.xlabel("Phase")
        plt.ylabel("Brightness")
        plt.show()

    def _get_phase(self, pivot_time: float, ref_time: float, period: float) -> float:
        return (pivot_time - ref_time) * 24 % period / period

    def _get_grid_size(self, bins: list[LightcurveBin]) -> tuple[int, int]:
        n = len(bins)
        if n == 0:
            return (0, 0)
        elif n == 1:
            return (1, 1)

        columns = min(4, n)
        rows = math.ceil(n / columns)

        while columns > 1 and rows < columns:
            columns -= 1
            rows = math.ceil(n / columns)

        return (rows, columns)
