import matplotlib.pyplot as plt
import numpy as np
from astropy.timeseries import LombScargle

from astrofit.model import LightcurveBin


class FrequencyDecomposer:
    def decompose_bins(
        self,
        lightcurve_bins: list[LightcurveBin],
        fourier_nterms: int,
        top_k: int,
        max_freq: float | None = None,
        show_plot: bool = False,
    ) -> list[np.ndarray]:
        return self._decompose_bins(lightcurve_bins, fourier_nterms, top_k, max_freq, show_plot)

    def decompose_bin(
        self,
        lightcurve_bin: LightcurveBin,
        fourier_nterms: int,
        top_k: int,
        max_freq: float | None = None,
        show_plot: bool = False,
    ) -> np.ndarray:
        return self._decompose_bins([lightcurve_bin], fourier_nterms, top_k, max_freq, show_plot)[0]

    def _decompose_bins(
        self,
        lightcurve_bins: list[LightcurveBin],
        fourier_nterms: int,
        top_k: int,
        max_freq: float | None,
        show_plot: bool,
    ) -> list[np.ndarray]:
        ret_data = []
        for lightcurve_bin in lightcurve_bins:
            ret_data.append(self._decompose_bin(lightcurve_bin, fourier_nterms, top_k, max_freq, show_plot))

        return ret_data

    def _decompose_bin(
        self,
        lightcurve_bin: LightcurveBin,
        fourier_nterms: int,
        top_k: int,
        max_freq: float | None,
        show_plot: bool,
    ) -> np.ndarray:
        frequency, power = LombScargle(
            lightcurve_bin.times,
            lightcurve_bin.brightnesses,
            nterms=fourier_nterms,
        ).autopower(method="chi2", maximum_frequency=max_freq)

        if show_plot:
            plt.plot(frequency, power)
            plt.xlabel("Frequency")
            plt.ylabel("Power")
            plt.title(f"Lomb-Scargle periodogram for {lightcurve_bin}")
            plt.show()

        idx = np.argsort(power)[::-1][:top_k]

        return np.array([frequency[idx], power[idx]]).T
