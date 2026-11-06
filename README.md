# Jet fuel hedging project

## What this starter does

The current `data.csv` contains natural-gas (`ng`) futures contracts, with
contract codes in `Prefix` and prices in `Last`. It does not contain jet-fuel
spot prices, so this starter covers only the first two project steps:

1. Plot a recent futures-price curve against contract maturity.
2. Compare the first usable curve in each year and track the front-to-one-year
   futures spread. A positive spread means contango; a negative spread means
   backwardation.

The CSV does not state the price units in its column headers. Based on the
Henry Hub contract information in the email, prices are shown as USD per
MMBtu. The 10,000 MMBtu contract size is not applied to these per-unit price
charts.

The one-year spread uses the nearest available contract and the contract with
maturity exactly 12 months after it. This makes the spread comparable over
time. It is an initial description of the futures curve, not a jet-fuel hedge
or a claim about the strength of the relationship between natural gas and jet
fuel.

## Set up on macOS

Open this project folder in VS Code, then run these commands in its terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python base_code.py
```

In VS Code, choose **Python: Select Interpreter** from the Command Palette and
select the interpreter inside this folder's `.venv` directory.

The script writes three charts and an animated GIF into `outputs/`:

- `curve_latest.png`
- `curves_by_year.png` (quarterly curve snapshots grouped by year; each year has its own price-axis scale)
- `curve_animation.gif` (one usable snapshot per month; the price axis adjusts each month)
- `curve_regimes.png` (monthly spreads with a three-month moving average)

To view them, open the `outputs` folder in the VS Code Explorer and click a
PNG or GIF. You can also open the folder in Finder from the project terminal:

```bash
open outputs
```

The source CSV stays unchanged. `Assumptions_goals.md` records the later
hedging calculations and remaining project steps.
