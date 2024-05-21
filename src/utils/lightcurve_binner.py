from src.model import Asteroid, Lightcurve


class LightcurveBinner:
    def bin_lightcurves_from_asteroid(
        self, asteroid: Asteroid, max_time_diff: float, min_bin_size: int | None = None
    ) -> list[list[Lightcurve]]:
        return self._bin_lightcurves(asteroid.lightcurves, max_time_diff, min_bin_size)

    def bin_lightcurves(
        self, lightcurves: list[Lightcurve], max_time_diff: float, min_bin_size: int | None = None
    ) -> list[list[Lightcurve]]:
        return self._bin_lightcurves(lightcurves, max_time_diff, min_bin_size)

    def _bin_lightcurves(
        self, lightcurves: list[Lightcurve], max_time_diff: float, min_bin_size: int | None = None
    ) -> list[list[Lightcurve]]:
        bins: list[list[Lightcurve]] = [[]]

        curr_bin = 0
        bin_start = None
        for lc in lightcurves:
            if bin_start is None:
                bin_start = lc.first_JD

            if lc.last_JD - bin_start > max_time_diff:
                curr_bin += 1
                bin_start = lc.first_JD
                bins.append([])

            bins[curr_bin].append(lc)

        if min_bin_size is not None:
            bins = self._filter_bins(bins, min_bin_size)

        return bins

    def _filter_bins(self, bins: list[list[Lightcurve]], min_n: int) -> list[list[Lightcurve]]:
        return [bin for bin in bins if len(bin) >= min_n]
