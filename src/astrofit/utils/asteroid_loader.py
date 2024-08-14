import json
from pathlib import Path

import pandas as pd

from astrofit.model import Asteroid

SPIN_PARAMS_FILE = "spin_params.json"
LC_FILE = "lc.json"


class AsteroidLoader:
    def __init__(self, data_dir: Path | str) -> None:
        self._data_dir = Path(data_dir)
        self._asteroids_dir = self._data_dir / "asteroids"

        self._asteroids_df = self._load_asteroids_df()
        self._available_asteroids = self._get_available_asteroids()

    def get_asteroid_info(self, asteroid_name: str) -> dict:
        if asteroid_name not in self._available_asteroids:
            raise ValueError(f"Asteroid {asteroid_name} not found!")

        return self._available_asteroids[asteroid_name]

    def load_asteroid(self, asteroid_name: str) -> Asteroid:
        asteroid_info = self.get_asteroid_info(asteroid_name)

        asteroid_dir = self._asteroids_dir / asteroid_name

        asteroid_data_path = asteroid_dir / LC_FILE
        if not asteroid_data_path.exists():
            raise FileNotFoundError(f"Missing light curve data for asteroid {asteroid_name}!")

        asteroid_id, period = asteroid_info["id"], asteroid_info["period"]
        with open(asteroid_data_path, "r") as f:
            asteroid_data = json.load(f)

        spin_param_file = asteroid_dir / SPIN_PARAMS_FILE
        if not spin_param_file.exists():
            raise FileNotFoundError(f"Missing spin params data for asteroid {asteroid_name}!")

        with open(spin_param_file, "r") as f:
            spin_params = json.load(f)

        period, lambd, beta = spin_params["period"], spin_params["lambda"], spin_params["beta"]

        return Asteroid.from_lightcurves(
            id=asteroid_id, name=asteroid_name, period=period, lambd=lambd, beta=beta, data=asteroid_data
        )

    def load_asteroids(self) -> dict[str, Asteroid]:
        return {name: self.load_asteroid(name) for name in self._available_asteroids}

    @property
    def available_asteroids(self) -> dict[str, dict]:
        return self._available_asteroids

    @property
    def asteroids_df(self) -> pd.DataFrame:
        return self._asteroids_df

    def _load_asteroids_df(self) -> pd.DataFrame:
        asteroid_csv = self._data_dir / "asteroids.csv"
        if not asteroid_csv.exists():
            raise FileNotFoundError(f"Could not find `asteroids.csv` in {self._data_dir}!")

        asteroids_df = pd.read_csv(asteroid_csv, index_col=0)
        asteroids_df.dropna(subset=["number"], inplace=True)
        asteroids_df["number"] = asteroids_df["number"].astype(int)

        return asteroids_df

    def _get_available_asteroids(self) -> dict[str, dict]:
        available_asteroids = {}
        for directory in self._asteroids_dir.iterdir():
            if not directory.is_dir():
                continue

            asteroid_name = directory.name.split("_")[0]
            work_name = directory.name

            res = self._asteroids_df[self._asteroids_df["name"] == asteroid_name]
            if len(res) != 1:
                raise ValueError(f"Found multiple asteroids with name {asteroid_name} (work name: {work_name})")

            (asteroid_num,) = res["number"]

            if not (directory / SPIN_PARAMS_FILE).exists():
                raise FileNotFoundError(f"Missing {SPIN_PARAMS_FILE} for {work_name}")

            with open(directory / SPIN_PARAMS_FILE, "r") as f:
                spin_params = json.load(f)

            period, lambd, beta = spin_params["period"], spin_params["lambda"], spin_params["beta"]

            available_asteroids[work_name] = {
                "id": asteroid_num,
                "name": asteroid_name,
                "period": period,
                "lambda": lambd,
                "beta": beta,
            }

        available_asteroids = {k: available_asteroids[k] for k in sorted(available_asteroids)}

        return available_asteroids
