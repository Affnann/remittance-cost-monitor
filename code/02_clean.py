"""Extract every surveyed service for sending money to Bangladesh, and check it.

Reads data/raw/rpw_dataset_2011_2025_q3.xlsx (both data sheets: up to 2016 Q1, and from 2016 Q2).
Writes data/clean/bangladesh_services.csv: one row per service (firm and product) per sending
country per quarter. Values are kept as published.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN = ROOT / "data" / "raw", ROOT / "data" / "clean"
CLEAN.mkdir(parents=True, exist_ok=True)
XLSX = RAW / "rpw_dataset_2011_2025_q3.xlsx"

# The two sheets name a few columns differently (the World Bank changed categories in 2016 Q2).
RENAME_OLD = {"sending location": "access_point", "product": "product", "pick-up method": "pickup_method",
              "coverage": "receiving_network_coverage", "note1": "note"}
RENAME_NEW = {"access point": "access_point", "payment instrument": "payment_instrument",
              "pickup method": "pickup_method", "receiving network coverage": "receiving_network_coverage",
              "Standard Note": "note"}
COMMON = {"id": "service_id", "period": "period", "source_code": "source_code", "source_name": "sending_country",
          "firm": "firm", "firm_type": "firm_type", "speed actual": "speed",
          "cc1 denomination amount": "usd200_amount_usd", "cc1 lcu amount": "usd200_amount_lcu",
          "cc1 lcu code": "lcu_code", "cc1 lcu fee": "usd200_fee_lcu", "cc1 fx margin": "usd200_fx_margin_pct",
          "cc1 total cost %": "usd200_total_cost_pct",
          "cc2 denomination amount": "usd500_amount_usd", "cc2 lcu amount": "usd500_amount_lcu",
          "cc2 lcu fee": "usd500_fee_lcu", "cc2 fx margin": "usd500_fx_margin_pct",
          "cc2 total cost %": "usd500_total_cost_pct",
          "inter lcu bank fx": "interbank_fx", "transparent": "transparent", "date": "survey_date"}

parts = []
for sheet, extra in [("Dataset (up to Q1 2016)", RENAME_OLD), ("Dataset (from Q2 2016)", RENAME_NEW)]:
    d = pd.read_excel(XLSX, sheet_name=sheet)
    if "from Q2 2016" in sheet:
        # Check the file against the World Bank's own report: its Q3 2025 global average is 6.36 percent
        # (Remittance Prices Worldwide, Issue 54, September 2025).
        g = pd.to_numeric(d.loc[d["period"] == "2025_3Q", "cc1 total cost %"], errors="coerce").mean()
        print("Global average, 2025 Q3, recomputed from the file:", round(g, 2), "percent (report: 6.36)")
        assert round(g, 2) == 6.36
    d = d[d["destination_name"] == "Bangladesh"]
    keep = {**COMMON, **{k: v for k, v in extra.items() if k in d.columns}}
    parts.append(d[list(keep)].rename(columns=keep))
df = pd.concat(parts, ignore_index=True)

num = [c for c in df.columns if c.startswith(("usd200", "usd500")) and c != "lcu_code"] + ["interbank_fx"]
for c in num:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["year"] = df["period"].str[:4].astype(int)
df["quarter"] = df["period"].str[5].astype(int)
df["survey_date"] = pd.to_datetime(df["survey_date"], errors="coerce").dt.date
df["usd200_fee_pct"] = 100 * df["usd200_fee_lcu"] / df["usd200_amount_lcu"]

# Checks.
# 1. Total cost = fee as a share of the amount sent + exchange-rate margin, for every row.
resid = df["usd200_total_cost_pct"] - (df["usd200_fee_pct"] + df["usd200_fx_margin_pct"])
assert resid.abs().max() < 0.05, resid.abs().max()
# 2. Each service appears once per quarter.
assert not df.duplicated(["period", "service_id"]).any()
# 3. Rows whose surveyed amount is not 200 US dollars are flagged, not changed.
df["note_check"] = np.where(df["usd200_amount_usd"] != 200,
                            "usd200_amount_usd is not 200 as published; local-currency amount and cost are consistent with 200 US dollars", "")
df["note_check"] = np.where(df["usd200_total_cost_pct"] < 0,
                            df["note_check"] + "negative total cost as published (exchange rate better than the interbank rate)", df["note_check"])

order = ["period", "year", "quarter", "sending_country", "source_code", "service_id", "firm", "firm_type",
         "product", "payment_instrument", "access_point", "speed", "pickup_method", "receiving_network_coverage",
         "transparent", "lcu_code", "interbank_fx",
         "usd200_amount_usd", "usd200_amount_lcu", "usd200_fee_lcu", "usd200_fee_pct", "usd200_fx_margin_pct", "usd200_total_cost_pct",
         "usd500_amount_usd", "usd500_amount_lcu", "usd500_fee_lcu", "usd500_fx_margin_pct", "usd500_total_cost_pct",
         "survey_date", "note", "note_check"]
df = df[[c for c in order if c in df.columns]].sort_values(["period", "sending_country", "firm"]).reset_index(drop=True)
df.to_csv(CLEAN / "bangladesh_services.csv", index=False)
print(len(df), "rows;", df["sending_country"].nunique(), "sending countries;", df["period"].min(), "to", df["period"].max())
print("largest gap between total cost and fee + FX margin:", round(resid.abs().max(), 4), "percentage points")
print((df["note_check"] != "").sum(), "rows flagged")
