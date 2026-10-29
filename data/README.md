# Data

## Source

- **World Bank, Remittance Prices Worldwide (RPW), complete dataset**, file `rpw_dataset_2011_2025_q3.xlsx`, from the World Bank Data Catalog (dataset 0037898): https://datacatalog.worldbank.org/search/dataset/0037898/remittance-prices-worldwide
- **Downloaded:** October 29, 2026, by `code/01_download.py`. Coverage: 2011 Q1 to 2025 Q3.
- **Licence:** Creative Commons Attribution 4.0 (CC BY 4.0), as listed on the Data Catalog page. The file's own "Terms of Use" sheet still carries an older label and links to retired World Bank short links (go.worldbank.org, which no longer resolves); this project follows the licence on the current catalog page.
- **Methodology:** the World Bank surveys the price of sending the equivalent of 200 and 500 US dollars with each provider on each route, every quarter. See the "Methodology" and "Legend" sheets of the file and the World Bank's quarterly report.

The World Bank's complete file is not included here because of its size (about 50 MB).

## Clean dataset (`clean/bangladesh_services.csv`)

All rows of both data sheets ("up to Q1 2016" and "from Q2 2016") whose destination is Bangladesh: 7,615 rows. Values are kept as published. The World Bank renamed some categories in 2016 Q2; columns that exist only in one period are empty in the other.

| Column | Meaning |
|---|---|
| `period`, `year`, `quarter` | Survey quarter |
| `sending_country`, `source_code` | Country the money is sent from, and its ISO code |
| `service_id` | World Bank id of the service |
| `firm`, `firm_type` | Provider and its type (bank, money transfer operator, post office, mobile operator), as published |
| `product` | Type of product (up to 2016 Q1 only) |
| `payment_instrument` | How the sender pays (from 2016 Q2 only) |
| `access_point` | Where the service can be used ("sending location" before 2016 Q2) |
| `speed`, `pickup_method`, `receiving_network_coverage` | How fast the money arrives, how it is collected, and how wide the network is in Bangladesh |
| `transparent` | Whether the provider disclosed the exchange rate it applied |
| `lcu_code`, `interbank_fx` | Sending country's currency and the benchmark (interbank) exchange rate used |
| `usd200_amount_usd`, `usd200_amount_lcu` | Amount surveyed: 200 US dollars, and the same amount in the sending currency |
| `usd200_fee_lcu`, `usd200_fee_pct` | Fee in the sending currency, and as a percentage of the amount (computed here) |
| `usd200_fx_margin_pct` | How much worse the provider's exchange rate was than the benchmark rate, in percent |
| `usd200_total_cost_pct` | Total cost in percent of the amount (fee plus exchange-rate margin) |
| `usd500_*` | The same for 500 US dollars |
| `survey_date` | Day the price was collected |
| `note` | The World Bank's note on the service |
| `note_check` | This project's flag for rows kept as published but unusual (see the main README) |

## Checks

`code/02_clean.py` stops with an error if any of these fail:

1. The global average for 2025 Q3 recomputed from the file equals 6.36 percent, the value in the World Bank's report (Remittance Prices Worldwide, Issue 54, September 2025).
2. For every Bangladesh row, total cost equals fee percent plus exchange-rate margin to within 0.05 percentage points (the largest gap is 0.0114).
3. No service appears twice in the same quarter.
