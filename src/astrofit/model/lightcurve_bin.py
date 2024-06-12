from __future__ import annotations

from functools import cached_property
from typing import Iterator

from pydantic import BaseModel

from astrofit.model.lightcurve import Lightcurve


class LightcurveBin(BaseModel):
    lightcurves: list[Lightcurve]

    def __len__(self) -> int:
        return len(self.lightcurves)

    def __iter__(self) -> Iterator[Lightcurve]:
        return iter(self.lightcurves)

    def __getitem__(self, ind) -> Lightcurve:
        return self.lightcurves[ind]

    def __repr__(self) -> str:
        return (
            f"LightcurveBin(lightcurves={len(self.lightcurves)}, period={self.get_period():.5f}h, points={self.points_count})"
        )

    def __lt__(self, other: LightcurveBin) -> bool:
        return len(self) < len(other)

    def __eq__(self, other: LightcurveBin) -> bool:
        return len(self) == len(other)

    def get_period(self, in_hours: bool | None = None) -> float:
        """
        Get the period of the light curve converted to hours if less than 1 day.
        """
        diff = self.last_JD - self.first_JD

        if in_hours is None:
            if diff < 1:
                return diff * 24
            else:
                return diff

        return diff * 24 if in_hours else diff

    @cached_property
    def first_JD(self) -> float:
        return self.lightcurves[0].first_JD

    @cached_property
    def last_JD(self) -> float:
        return self.lightcurves[-1].last_JD

    @cached_property
    def points_count(self) -> int:
        return sum(len(lc) for lc in self.lightcurves)

    @cached_property
    def times(self) -> list[float]:
        times: list[float] = []
        for lc in self.lightcurves:
            times.extend(lc.time_arr)

        return times

    @cached_property
    def brightnesses(self) -> list[float]:
        brightnesses: list[float] = []
        for lc in self.lightcurves:
            brightnesses.extend(lc.brightness_arr)

        return brightnesses
