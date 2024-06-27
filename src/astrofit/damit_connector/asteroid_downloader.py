import json
from pathlib import Path
from random import choice

import pandas as pd
import requests
from bs4 import BeautifulSoup

DAMIT_URL = "https://astro.troja.mff.cuni.cz/projects/damit/?q="
LC_JSON_URI = "https://astro.troja.mff.cuni.cz/projects/damit/light_curves/exportAllForAsteroid/{}/json"

request_headers = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",  # noqa E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "http://www.google.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "http://www.google.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",  # noqa E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "http://www.google.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",  # noqa E501
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.apple.com",
    },
    {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.mozilla.org",
    },
]


class AsteroidDownloader:
    def __init__(self, data_dir: Path | str) -> None:
        self._data_dir = Path(data_dir)
        self._asteroids_dir = self._data_dir / "asteroids"

        self._asteroids_df = self._load_asteroids_df()

    def query_asteroid(self, query: str | int, exists_ok: bool = False) -> None:
        if isinstance(query, int):
            query = str(query)

        response = requests.get(DAMIT_URL + query, headers=choice(request_headers))
        soup = BeautifulSoup(response.content, "html.parser")

        print(f"Beginning asteroid extraction for: {query}...")
        self._extract_asteroid_info(soup, query, exists_ok)

    def _load_asteroids_df(self) -> pd.DataFrame:
        asteroid_csv = self._data_dir / "asteroids.csv"
        if not asteroid_csv.exists():
            raise FileNotFoundError(f"Could not find `asteroids.csv` in {self._data_dir}!")

        asteroids_df = pd.read_csv(asteroid_csv, index_col=0)
        asteroids_df.dropna(subset=["number"], inplace=True)
        asteroids_df["number"] = asteroids_df["number"].astype(int)

        return asteroids_df

    def _extract_asteroid_info(self, soup: BeautifulSoup, query: str, exists_ok: bool) -> None:
        table = soup.find("table", class_="damit-table-asteroids-browse")
        if table is None:
            print(f"No object found for query: {query}!")
            return None

        tbody = table.find("tbody")
        if tbody is None:
            raise ValueError(f"No tbody found for query: {query}")

        asteroid_name = self._get_asteroid_name(tbody)  # type: ignore
        if asteroid_name is None:
            raise ValueError(f"No asteroid name found for query: {query}\n")

        print(f"Found asteroid: {asteroid_name}")
        self._extract_row_models(asteroid_name, tbody, exists_ok)  # type: ignore
        print(f"Finished extracting asteroid {asteroid_name}!")

    def _get_asteroid_name(self, tbody: BeautifulSoup) -> str | None:
        tr = tbody.find("tr", class_="damit-asteroid-row")
        th = tr.find("th")  # type: ignore
        a = th.find("a")  # type: ignore

        return a.text.split(") ")[1].strip()  # type: ignore

    def _extract_row_models(self, asteroid_name: str, tbody: BeautifulSoup, exists_ok: bool) -> None:
        trs = tbody.find_all("tr", class_="damit-model-row")
        if len(trs) == 0:
            raise ValueError(f"No models found for asteroid {asteroid_name}")

        print(f"Found {len(trs)} models for {asteroid_name}, selecting the most recent one...")
        tr = trs[-1]

        period = self._get_period(tr)
        if period is None:
            raise ValueError(f"Period not found for asteroid {asteroid_name}")

        asteroid_dir = self._create_asteroid_dir(asteroid_name, exists_ok)
        self._download_lc_json(asteroid_name, asteroid_dir)
        self._save_period(period, asteroid_dir)

    def _match_span(self, tag: BeautifulSoup) -> bool:
        return (
            tag.name == "span"
            and tag.get("class", None) == ["damit-cursor-help"]
            and (tag.get("data-original-title", None) == "Period" or tag.get("title", None) == "Period")
        )

    def _get_period(self, tr: BeautifulSoup) -> float | None:
        tds = tr.find_all("td")
        for td in tds:
            span = td.find(self._match_span)
            if span is not None:
                return float(span.text.split()[0])

        return None

    def _create_asteroid_dir(self, asteroid_name: str, exists_ok: bool) -> Path:
        asteroid_dir = self._asteroids_dir / asteroid_name

        asteroid_dir.mkdir(parents=True, exist_ok=exists_ok)

        return asteroid_dir

    def _download_lc_json(self, asteroid_name: str, asteroid_dir: Path) -> None:
        (asteroid_id,) = self._asteroids_df.query(f"name == '{asteroid_name}'").index
        response = requests.get(LC_JSON_URI.format(asteroid_id), headers=choice(request_headers))

        lc_json = json.loads(response.content)
        lc_file = asteroid_dir / "lc.json"
        with open(lc_file, "w") as f:
            json.dump(lc_json, f, indent=4)

        print(f"Downloaded light curve JSON for asteroid {asteroid_name} to {lc_file}")

    def _save_period(self, period: float, asteroid_dir: Path) -> None:
        period_file = asteroid_dir / "period.txt"
        with open(period_file, "w") as f:
            f.write(str(period))

        print(f"Saved period for asteroid to {period_file}")
