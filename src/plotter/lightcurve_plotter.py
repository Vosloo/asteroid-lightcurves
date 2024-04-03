from matplotlib import pyplot as plt

from src.model import Lightcurve


class LightcurvePlotter:
    @staticmethod
    def plot_lightcurve(lightcurve: Lightcurve):
        """
        Plot the light curve.

        :param lightcurve: The light curve to plot.
        """
        lightcurve.plot()
        plt.show()

    @staticmethod
    def plot_lightcurves(lightcurves: list[Lightcurve], subplots: bool = False):
        """
        Plot the light curves.

        :param lightcurves: The light curves to plot.
        :param subplots: Whether to plot the light curves in subplots.
        """
        min_JD = None
        max_JD = None
        if subplots:
            _, axs = plt.subplots(len(lightcurves))

        for i, lc in enumerate(lightcurves):
            if min_JD is None or lc.first_JD < min_JD:
                min_JD = lc.first_JD
            if max_JD is None or lc.last_JD > max_JD:
                max_JD = lc.last_JD

            if subplots:
                ax = axs[i]
                lc.plot(ax=ax)
                ax.set_xlabel("Julian Date")
                ax.set_ylabel("Brightness")
            else:
                lc.plot()

        if min_JD is None or max_JD is None:
            raise ValueError("No light curves to plot!")

        diff = max_JD - min_JD
        if diff < 1:
            period = f"{diff * 24:.4f} hours"
        else:
            period = f"{diff:.4f} days"

        if not subplots:
            plt.xlabel("Julian Date")
            plt.ylabel("Brightness")
            plt.title(f"Lightcurves from {min_JD} to {max_JD} (period={period})")
        else:
            plt.tight_layout()

        plt.show()
