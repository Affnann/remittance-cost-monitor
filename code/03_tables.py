"""Tables and charts from data/clean/bangladesh_services.csv.

Corridor averages follow the World Bank's own method for a corridor: the simple average of the
total cost across all services surveyed on that route in that quarter. Costs are for sending
the equivalent of 200 US dollars unless stated otherwise.
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TAB, FIG = ROOT / "output" / "tables", ROOT / "figures"
TAB.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
SDG = 3.0  # Sustainable Development Goal 10.c: remittance costs below 3 percent

df = pd.read_csv(ROOT / "data" / "clean" / "bangladesh_services.csv")
cost = "usd200_total_cost_pct"

# 1. Corridor averages by quarter: total cost, and its two parts (fee and exchange-rate margin).
cq = (df.groupby(["period", "year", "quarter", "sending_country"])
        .agg(services=(cost, "size"), total_cost_pct=(cost, "mean"),
             fee_pct=("usd200_fee_pct", "mean"), fx_margin_pct=("usd200_fx_margin_pct", "mean"),
             cheapest_pct=(cost, "min"))
        .round(3).reset_index())
cq.to_csv(TAB / "corridor_by_quarter.csv", index=False)

# 2. All Bangladesh routes by year: simple average across services, and its parts.
yr = df.groupby("year").agg(services=(cost, "size"), total_cost_pct=(cost, "mean"),
                            fee_pct=("usd200_fee_pct", "mean"), fx_margin_pct=("usd200_fx_margin_pct", "mean"),
                            share_below_3pct=(cost, lambda s: (s < SDG).mean() * 100)).round(2)
yr.to_csv(TAB / "all_routes_by_year.csv")

# 3. Latest quarter: each corridor's average, cheapest service, and share of services below 3 percent.
last = df["period"].max()
lq = df[df["period"] == last]
latest = (lq.groupby("sending_country")
            .agg(services=(cost, "size"), average_cost_pct=(cost, "mean"), cheapest_cost_pct=(cost, "min"),
                 share_services_below_3pct=(cost, lambda s: (s < SDG).mean() * 100),
                 average_cost_usd_on_200=(cost, lambda s: 2 * s.mean()))
            .round(2).sort_values("average_cost_pct"))
cheapest = lq.loc[lq.groupby("sending_country")[cost].idxmin(), ["sending_country", "firm", "firm_type"]]
latest = latest.join(cheapest.set_index("sending_country").rename(columns={"firm": "cheapest_firm", "firm_type": "cheapest_firm_type"}))
latest.to_csv(TAB / f"latest_quarter_{last}.csv")

# 4. By type of firm, latest four quarters.
last4 = sorted(df["period"].unique())[-4:]
ft = (df[df["period"].isin(last4)].groupby("firm_type")
        .agg(services=(cost, "size"), average_cost_pct=(cost, "mean"),
             fee_pct=("usd200_fee_pct", "mean"), fx_margin_pct=("usd200_fx_margin_pct", "mean"))
        .round(2).sort_values("average_cost_pct"))
ft.to_csv(TAB / "by_firm_type_last_4_quarters.csv")

# 5. $200 versus $500: average cost by year.
amt = df.groupby("year")[["usd200_total_cost_pct", "usd500_total_cost_pct"]].mean().round(2)
amt.to_csv(TAB / "usd200_vs_usd500_by_year.csv")

# Figure 1: all routes by year, split into fee and exchange-rate margin.
fig, ax = plt.subplots(figsize=(7.5, 3.8))
ax.bar(yr.index, yr["fee_pct"], color="0.35", label="Fee")
ax.bar(yr.index, yr["fx_margin_pct"], bottom=yr["fee_pct"], color="0.75", label="Exchange-rate margin")
ax.axhline(SDG, color="black", linewidth=0.8, linestyle="--")
ax.text(yr.index.min() - 0.4, SDG + 0.15, "3% target", fontsize=8)
ax.set_ylabel("Cost of sending $200 (% of amount)")
ax.legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(0.12, 1))
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(FIG / "cost_by_year.png", dpi=200)

# Figure 2: latest quarter by corridor.
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(latest.index, latest["average_cost_pct"], color="0.35")
ax.axvline(SDG, color="black", linewidth=0.8, linestyle="--")
ax.set_xlabel(f"Average cost of sending $200 to Bangladesh, {last.replace('_', ' ')} (% of amount)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(FIG / "latest_quarter_by_corridor.png", dpi=200)

pd.set_option("display.width", 200)
print(yr.to_string()); print(latest.to_string()); print(ft.to_string()); print(amt.tail(5).to_string())
