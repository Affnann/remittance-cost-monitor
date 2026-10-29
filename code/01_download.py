"""Download the World Bank's Remittance Prices Worldwide (RPW) complete dataset.

Source: World Bank Data Catalog, dataset 0037898 (licence: CC BY 4.0).
Saves data/raw/rpw_dataset_2011_2025_q3.xlsx (about 50 MB; not kept in the repository because of
its size). Covers 2011 Q1 to 2025 Q3.
"""
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
URL = "https://datacatalogfiles.worldbank.org/ddh-published/0037898/DR0095523/rpw_dataset_2011_2025_q3.xlsx"

out = RAW / "rpw_dataset_2011_2025_q3.xlsx"
with requests.get(URL, stream=True, timeout=600) as r:
    r.raise_for_status()
    with open(out, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
print("Saved", out, out.stat().st_size // 1_000_000, "MB")
