import seaborn as sns
from matplotlib import pyplot as plt

from astrofit.model import Lightcurve, LightcurveBin

plt.rcParams["figure.figsize"] = (12, 6)
sns.set_theme()


class LightcurvePlotter:
    def plot_lightcurve(self, lightcurve: Lightcurve):
        """
        Plot the light curve.

        :param lightcurve: The light curve to plot.
        """
        lightcurve.plot(color=sns.color_palette("icefire")[0])
        plt.show()

    def plot_lightcurves(self, lightcurves: list[Lightcurve] | LightcurveBin, split_plots: bool = False):
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
                lc.plot(color=colors[i])
                plt.show()
            else:
                lc.plot(color=colors[i])

        if min_JD is None or max_JD is None:
            raise ValueError("No light curves to plot!")

        if split_plots:
            return

        diff = max_JD - min_JD
        if diff < 1:
            _range = f"{diff * 24:.4f} hours"
        else:
            _range = f"{diff:.4f} days"

        plt.xlabel("Julian Date")
        plt.ylabel("Brightness")
        plt.title(f"{len(lightcurves)} lightcurves - range={_range}")

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
