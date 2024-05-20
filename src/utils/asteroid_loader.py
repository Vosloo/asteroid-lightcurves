import json
import pandas as pd

from constants import ASTEROIDS_DIR, DATA_DIR
from src.model import Asteroid

PERIOD_FILE = "period.txt"
LC_FILE = "lc.json"


class AsteroidLoader:
    def __init__(self) -> None:
        self._asteroids_df = self._load_asteroids_df()
        self._available_asteroids = self._get_available_asteroids()

    def get_asteroid_info(self, asteroid_name: str) -> dict:
        if asteroid_name not in self._available_asteroids:
            raise ValueError(f"Asteroid {asteroid_name} not found!")

        return self._available_asteroids[asteroid_name]

    def load_asteroid(self, asteroid_name: str) -> Asteroid:
        asteroid_info = self.get_asteroid_info(asteroid_name)

        asteroid_data_path = ASTEROIDS_DIR / asteroid_name / LC_FILE
        if not asteroid_data_path.exists():
            raise FileNotFoundError(f"Missing light curve data for asteroid {asteroid_name}!")

        asteroid_id, period = asteroid_info["id"], asteroid_info["period"]
        with open(asteroid_data_path, "r") as f:
            asteroid_data = json.load(f)

        return Asteroid.from_lightcurves(id=asteroid_id, name=asteroid_name, period=period, data=asteroid_data)

    @property
    def available_asteroids(self) -> dict[str, dict]:
        return self._available_asteroids

    def _load_asteroids_df(self) -> pd.DataFrame:
        asteroid_csv = DATA_DIR / "asteroids.csv"
        if not asteroid_csv.exists():
            raise FileNotFoundError(f"Could not find `asteroids.csv` in {DATA_DIR}!")

        asteroids_df = pd.read_csv(asteroid_csv, index_col=0)
        asteroids_df.dropna(subset=["number"], inplace=True)
        asteroids_df["number"] = asteroids_df["number"].astype(int)

        return asteroids_df

    def _get_available_asteroids(self) -> dict[str, dict]:
        available_asteroids = {}
        for directory in ASTEROIDS_DIR.iterdir():
            if not directory.is_dir():
                continue

            asteroid_name = directory.name.split("_")[0]
            work_name = directory.name

            res = self._asteroids_df.query(f"name == '{asteroid_name}'")
            if len(res) != 1:
                raise ValueError(f"Found multiple asteroids with name {asteroid_name} (work name: {work_name})")

            (asteroid_num,) = res["number"]

            if not (directory / PERIOD_FILE).exists():
                raise FileNotFoundError(f"Missing {PERIOD_FILE} for {work_name}")

            with open(directory / PERIOD_FILE, "r") as f:
                period = float(f.read().strip())

            available_asteroids[work_name] = {"id": asteroid_num, "name": asteroid_name, "period": period}

        available_asteroids = {k: available_asteroids[k] for k in sorted(available_asteroids)}

        return available_asteroids
