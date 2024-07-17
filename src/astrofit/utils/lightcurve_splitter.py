import numpy as np

from astrofit.model import Lightcurve, Point


class LightcurveSplitter:
    def split_lightcurves(
        self,
        lightcurves: list[Lightcurve],
        max_hours_diff: float,
        min_no_points: int | None = None,
    ) -> list[Lightcurve]:
        splitted_lightcurves = []
        for lightcurve in lightcurves:
            splitted_lightcurves.extend(self._split_lightcurve(lightcurve, max_hours_diff, min_no_points))

        return splitted_lightcurves

    def split_lightcurve(
        self,
        lightcurve: Lightcurve,
        max_hours_diff: float,
        min_no_points: int | None = None,
    ) -> list[Lightcurve]:
        return self._split_lightcurve(lightcurve, max_hours_diff, min_no_points)

    def _split_lightcurve(
        self,
        lightcurve: Lightcurve,
        max_hours_diff: float,
        min_no_points: int | None = None,
    ) -> list[Lightcurve]:
        splitted_lightcurves = []

        curr_points = []
        for point in lightcurve.points:
            if not curr_points:
                curr_points.append(point)
                continue

            # In hours
            if 24 * (point.JD - curr_points[-1].JD) > max_hours_diff:
                if (filtered_points := self._filter_points(curr_points, min_no_points)) is not None:
                    splitted_lightcurves.append(Lightcurve.from_points(og_lightcurve=lightcurve, points=filtered_points))

                curr_points = []

            curr_points.append(point)

        if curr_points and (min_no_points is None or len(curr_points) >= min_no_points):
            splitted_lightcurves.append(Lightcurve.from_points(og_lightcurve=lightcurve, points=curr_points))

        return splitted_lightcurves

    def _filter_points(self, points: list[Point], min_no_points: int | None) -> list[Point] | None:
        if min_no_points is not None and len(points) < min_no_points:
            return None

        brightnesses = np.array([point.brightness for point in points])

        median_brightness = np.median(brightnesses)
        median_absolute_dev = np.median(np.abs(brightnesses - median_brightness))

        if median_absolute_dev == 0:
            # Use mean absolute deviation instead
            mean_absolute_dev = np.mean(np.abs(brightnesses - median_brightness))
            modified_z_score = 0.7979 * (brightnesses - median_brightness) / mean_absolute_dev
        else:
            modified_z_score = 0.6745 * (brightnesses - median_brightness) / median_absolute_dev

        filtered = []
        for point, z_score in zip(points, modified_z_score):
            if z_score < -3.5 or z_score > 3.5:
                # Outlier
                continue

            filtered.append(point)

        if min_no_points is not None and len(filtered) < min_no_points:
            return None

        return filtered
