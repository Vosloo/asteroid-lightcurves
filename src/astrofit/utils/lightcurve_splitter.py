from astrofit.model import Lightcurve


class LightcurveSplitter:
    def split_lightcurves(
        self,
        lightcurves: list[Lightcurve],
        max_time_diff: float,
        min_no_points: int | None = None,
    ) -> list[Lightcurve]:
        splitted_lightcurves = []
        for lightcurve in lightcurves:
            splitted_lightcurves.extend(self._split_lightcurve(lightcurve, max_time_diff, min_no_points))

        return splitted_lightcurves

    def split_lightcurve(
        self,
        lightcurve: Lightcurve,
        max_time_diff: float,
        min_no_points: int | None = None,
    ) -> list[Lightcurve]:
        return self._split_lightcurve(lightcurve, max_time_diff, min_no_points)

    def _split_lightcurve(
        self,
        lightcurve: Lightcurve,
        max_time_diff: float,
        min_no_points: int | None = None,
    ) -> list[Lightcurve]:
        splitted_lightcurves = []

        curr_points = []
        for point in lightcurve.points:
            if not curr_points:
                curr_points.append(point)
                continue

            if point.JD - curr_points[0].JD > max_time_diff:
                if min_no_points is None or len(curr_points) >= min_no_points:
                    splitted_lightcurves.append(Lightcurve.from_splitted_lightcurve(lightcurve, curr_points))

                curr_points = []

            curr_points.append(point)

        if curr_points and (min_no_points is None or len(curr_points) >= min_no_points):
            splitted_lightcurves.append(Lightcurve.from_splitted_lightcurve(lightcurve, curr_points))

        return splitted_lightcurves
