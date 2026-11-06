# BASE CODE FOR NATURAL GAS FUTURES CURVES

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import pandas as pd
import numpy as np 
import random 
import math


DATA_FILE = Path(__file__).parent / "data.csv"
OUTPUT_DIR = Path(__file__).parent / "outputs"
PRICE_COLOR = "#285f78"
MONTH_CODES = {
    "f": 1,
    "g": 2,
    "h": 3,
    "j": 4,
    "k": 5,
    "m": 6,
    "n": 7,
    "q": 8,
    "u": 9,
    "v": 10,
    "x": 11,
    "z": 12,
}


def style_axes(ax: plt.Axes) -> None:
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#d9e1e5", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def load_futures_data(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    required_columns = {"Time", "Last", "Prefix"}
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {sorted(missing_columns)}")

    data["Time"] = pd.to_datetime(data["Time"], format="%m/%d/%Y")
    data["Last"] = pd.to_numeric(data["Last"], errors="raise")
    prefixes = data["Prefix"].astype(str).str.lower()

    valid_prefixes = prefixes.str.fullmatch(r"ng[fghjkmnquvxz]\d{2}")
    if not valid_prefixes.all():
        bad_prefixes = sorted(prefixes[~valid_prefixes].unique())
        raise ValueError(f"Unexpected natural-gas contract codes: {bad_prefixes[:5]}")

    contract_month = prefixes.str[2].map(MONTH_CODES)
    contract_year = 2000 + pd.to_numeric(prefixes.str[-2:], errors="raise")
    data["Maturity"] = contract_year * 12 + contract_month - 1
    return data


def month_index(date: pd.Timestamp) -> int:
    return date.year * 12 + date.month - 1


def curve_for_date(data: pd.DataFrame, date: pd.Timestamp) -> pd.DataFrame:
    current_month = month_index(date)
    contracts = data.loc[data["Time"] == date].copy()
    contracts["Months_to_maturity"] = contracts["Maturity"] - current_month
    return contracts.loc[
        contracts["Months_to_maturity"].between(0, 12)
    ].sort_values("Maturity")


def save_latest_curve(data: pd.DataFrame) -> None:
    dates = sorted(data["Time"].drop_duplicates(), reverse=True)
    curve = pd.DataFrame()
    curve_date = None
    for date in dates:
        candidate = curve_for_date(data, date)
        if len(candidate) >= 8:
            curve = candidate
            curve_date = date
            break

    if curve_date is None:
        raise ValueError("No date has at least 8 contract prices in the next 12 months.")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    last_month = int(curve["Months_to_maturity"].max())
    ax.plot(
        curve["Months_to_maturity"],
        curve["Last"],
        marker="o",
        markersize=5,
        linewidth=2,
        color=PRICE_COLOR,
    )
    ax.set(
        title=f"Henry Hub natural gas futures on {curve_date:%B %d, %Y}",
        xlabel="Months to contract maturity",
        ylabel="Futures price (USD/MMBtu)",
        xlim=(0.5, last_month + 0.5),
        xticks=range(1, last_month + 1, 2),
    )
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "curve_latest.png", dpi=150)
    plt.close(fig)
    print(f"Latest usable curve: {curve_date:%Y-%m-%d}")


def save_annual_curves(data: pd.DataFrame) -> None:
    yearly_curves = []
    quarter_months = {1: 1, 2: 4, 3: 7, 4: 10}
    quarter_colors = {
        1: "#3B6FB6",
        2: "#E08E45",
        3: "#4C956C",
        4: "#C8553D",
    }

    years = sorted(data["Time"].dt.year.unique())
    for year in years:
        year_data = data.loc[data["Time"].dt.year == year]
        for quarter, month in quarter_months.items():
            month_dates = sorted(
                year_data.loc[year_data["Time"].dt.month == month, "Time"].unique()
            )
            for date in month_dates:
                curve = curve_for_date(data, pd.Timestamp(date))
                if len(curve) >= 8:
                    yearly_curves.append(
                        (year, quarter, pd.Timestamp(date), curve)
                    )
                    break

    if not yearly_curves:
        raise ValueError("No quarters have a futures curve with at least 8 prices.")

    columns = 3
    years = sorted({year for year, _, _, _ in yearly_curves})
    rows = (len(years) + columns - 1) // columns
    fig, axes = plt.subplots(
        rows,
        columns,
        figsize=(12, rows * 2.5),
        sharex=True,
    )
    axes = axes.flatten() if hasattr(axes, "flatten") else [axes]

    used_axes = []
    for index, year in enumerate(years):
        row, column = divmod(index, columns)
        remaining_years = len(years) - row * columns
        if remaining_years == 1 and columns > 1:
            column = columns // 2
        ax = axes[row * columns + column]
        used_axes.append(ax)
        this_year = [
            (quarter, date, curve)
            for curve_year, quarter, date, curve in yearly_curves
            if curve_year == year
        ]
        for quarter, _, curve in this_year:
            ax.plot(
                curve["Months_to_maturity"],
                curve["Last"],
                color=quarter_colors[quarter],
                linewidth=1.6,
                label=f"Q{quarter}",
            )
        ax.set_title(str(year), loc="left", fontsize=10)
        ax.set_xlim(0.5, 12.5)
        ax.set_xticks([1, 4, 7, 10, 12])
        style_axes(ax)

    for ax in axes:
        if ax not in used_axes:
            ax.remove()

    fig.suptitle("Henry Hub futures curves by year", fontsize=15, y=0.99)
    fig.text(
        0.5,
        0.958,
        "Quarterly snapshots: January, April, July, and October. Price axes vary by year.",
        ha="center",
        fontsize=9,
        color="#59666d",
    )
    fig.supxlabel("Months to contract maturity", y=0.1)
    fig.supylabel("Futures price (USD/MMBtu)")
    quarter_handles = [
        plt.Line2D(
            [0],
            [0],
            color=quarter_colors[quarter],
            linewidth=2,
            label=f"Q{quarter}",
        )
        for quarter in quarter_months
    ]
    fig.legend(
        handles=quarter_handles,
        title="Snapshot",
        loc="lower center",
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.5, 0.015),
    )
    fig.tight_layout(rect=(0.04, 0.08, 1, 0.94), h_pad=1.1, w_pad=1.0)
    fig.savefig(OUTPUT_DIR / "curves_by_year.png", dpi=150)
    plt.close(fig)


def save_curve_animation(data: pd.DataFrame) -> None:
    monthly_curves = []
    seen_months = set()

    for date, contracts in data.groupby("Time", sort=True):
        month_key = (date.year, date.month)
        if month_key in seen_months:
            continue

        current_month = month_index(date)
        curve = contracts.copy()
        curve["Months_to_maturity"] = curve["Maturity"] - current_month
        curve = curve.loc[curve["Months_to_maturity"].between(0, 12)].sort_values(
            "Maturity"
        )
        if len(curve) >= 8:
            monthly_curves.append((date, curve))
            seen_months.add(month_key)

    if not monthly_curves:
        raise ValueError("No monthly futures curves have at least 8 contract prices.")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    (line,) = ax.plot([], [], marker="o", markersize=4, linewidth=2, color=PRICE_COLOR)
    ax.set(
        title="Henry Hub natural gas futures",
        xlabel="Months to contract maturity",
        ylabel="Futures price (USD/MMBtu)",
        xlim=(0, 12),
        xticks=range(0, 13, 2),
    )
    style_axes(ax)
    ax.text(
        0.99,
        0.97,
        "Axes adjust to available maturities and prices",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8,
        color="#59666d",
    )

    def update(frame: int):
        date, curve = monthly_curves[frame]
        months = curve["Months_to_maturity"]
        prices = curve["Last"]
        line.set_data(months, prices)
        last_month = int(months.max())
        ax.set_xlim(0.5, last_month + 0.5)
        ax.set_xticks(range(1, last_month + 1, 2))
        price_min = prices.min()
        price_max = prices.max()
        padding = max((price_max - price_min) * 0.18, 0.1)
        ax.set_ylim(price_min - padding, price_max + padding)
        ax.set_title(f"Henry Hub natural gas futures on {date:%B %Y}")
        return (line,)

    animation = FuncAnimation(
        fig,
        update,
        frames=len(monthly_curves),
        interval=250,
        blit=False,
        repeat=True,
    )
    animation.save(OUTPUT_DIR / "curve_animation.gif", writer=PillowWriter(fps=4))
    plt.close(fig)
    print(
        f"Curve animation: {len(monthly_curves)} monthly snapshots, "
        f"{monthly_curves[0][0]:%Y-%m} to {monthly_curves[-1][0]:%Y-%m}"
    )


def save_regime_history(data: pd.DataFrame) -> None:
    spreads = []
    for date, contracts in data.groupby("Time", sort=True):
        current_month = month_index(date)
        upcoming = contracts.loc[contracts["Maturity"] >= current_month].sort_values(
            "Maturity"
        )
        if upcoming.empty:
            continue

        front = upcoming.iloc[0]
        one_year_maturity = front["Maturity"] + 12
        back = upcoming.loc[upcoming["Maturity"] == one_year_maturity]
        if not back.empty:
            spreads.append(
                {
                    "Date": date,
                    "Spread": back.iloc[0]["Last"] - front["Last"],
                }
            )

    spread_data = pd.DataFrame(spreads)
    if spread_data.empty:
        raise ValueError("No dates contain both front and one-year futures prices.")

    monthly_spreads = (
        spread_data.set_index("Date")["Spread"]
        .resample("ME")
        .mean()
        .dropna()
        .rename("Monthly_average")
        .to_frame()
    )
    monthly_spreads["Three_month_average"] = monthly_spreads[
        "Monthly_average"
    ].rolling(window=3, min_periods=2).mean()

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(
        monthly_spreads.index,
        monthly_spreads["Monthly_average"],
        color="#aebbc2",
        linewidth=1,
        marker="o",
        markersize=2.5,
        label="Monthly average",
    )
    ax.plot(
        monthly_spreads.index,
        monthly_spreads["Three_month_average"],
        color=PRICE_COLOR,
        linewidth=2,
        label="Three-month average",
    )
    ax.axhline(0, color="#4b555a", linewidth=1, linestyle="--")
    ax.set(
        title="Front-to-one-year futures spread by month",
        xlabel="Date",
        ylabel="One-year price minus front price (USD/MMBtu)",
    )
    ax.text(
        0.01,
        0.98,
        "Positive spread: contango    Negative spread: backwardation",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        color="#59666d",
    )
    ax.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=2,
    )
    style_axes(ax)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(OUTPUT_DIR / "curve_regimes.png", dpi=150)
    plt.close(fig)
    print(f"Spread history: {spread_data['Date'].min():%Y-%m-%d} to "
          f"{spread_data['Date'].max():%Y-%m-%d}")


def main() -> None:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Could not find the data file: {DATA_FILE}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    futures = load_futures_data(DATA_FILE)
    save_latest_curve(futures)
    save_annual_curves(futures)
    save_curve_animation(futures)
    save_regime_history(futures)
    print(f"Charts saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
