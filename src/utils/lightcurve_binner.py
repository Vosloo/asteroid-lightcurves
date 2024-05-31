from src.model import Asteroid, Lightcurve

from .enums import BinningMethod


class LightcurveBinner:
    def bin_lightcurves_from_asteroid(
        self,
        asteroid: Asteroid,
        max_time_diff: float,
        binning_method: BinningMethod,
        min_bin_size: int | None = None,
    ) -> list[list[Lightcurve]]:
        return self._bin_lightcurves(asteroid.lightcurves, max_time_diff, binning_method, min_bin_size)

    def bin_lightcurves(
        self,
        lightcurves: list[Lightcurve],
        max_time_diff: float,
        binning_method: BinningMethod,
        min_bin_size: int | None = None,
    ) -> list[list[Lightcurve]]:
        return self._bin_lightcurves(lightcurves, max_time_diff, binning_method, min_bin_size)

    def _bin_lightcurves(
        self,
        lightcurves: list[Lightcurve],
        max_time_diff: float,
        binning_method: BinningMethod,
        min_bin_size: int | None = None,
    ) -> list[list[Lightcurve]]:
        bins: list[list[Lightcurve]] = [[]]

        curr_bin = 0
        last_bin_JD = None
        for lc in lightcurves:
            if last_bin_JD is None:
                if binning_method == BinningMethod.FIRST_TO_FIRST_DIFF:
                    last_bin_JD = lc.first_JD
                elif binning_method == BinningMethod.LAST_TO_FIRST_DIFF:
                    last_bin_JD = lc.last_JD

            if lc.first_JD - last_bin_JD > max_time_diff:
                curr_bin += 1

                if binning_method == BinningMethod.FIRST_TO_FIRST_DIFF:
                    last_bin_JD = lc.first_JD
                elif binning_method == BinningMethod.LAST_TO_FIRST_DIFF:
                    last_bin_JD = lc.last_JD

                bins.append([])

            bins[curr_bin].append(lc)

        if min_bin_size is not None:
            bins = self._filter_bins(bins, min_bin_size)

        return bins

    def _filter_bins(self, bins: list[list[Lightcurve]], min_n: int) -> list[list[Lightcurve]]:
        return [bin for bin in bins if len(bin) >= min_n]
