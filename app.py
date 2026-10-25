"""E-commerce Performance Dashboard.

A Streamlit dashboard for an e-commerce manager at a UK online retailer.
Dataset: Online Retail (UCI / Kaggle), transactions Dec 2010 - Dec 2011.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

# ---- page config ----
st.set_page_config(page_title="E-commerce Performance", page_icon="🛒", layout="wide")

TEAM_NAME = "Data Squad"          # TODO: replace with your actual team name
DATA_PERIOD = "Dec 2010 – Dec 2011 (Kaggle snapshot)"
REFRESH_NOTE = "Intended refresh: nightly; reviewed every Monday morning."


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("online_retail.csv", parse_dates=["InvoiceDate"])
    return df


raw = load_data()

# ---- data cleaning (documented in README) ----
# 1. drop cancellations / negative quantities / freebies, which are not real sales
df = raw[raw["Quantity"] > 0].copy()
df = df[df["UnitPrice"] > 0].copy()
df = df[~df["InvoiceNo"].astype(str).str.startswith("C")].copy()
# 2. one line item's value
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
# 3. week bucket for the trend chart
df["Week"] = df["InvoiceDate"].dt.to_period("W").dt.start_time

# ---- title + one-line caption (who it's for, what decision it supports) ----
st.title(f"🛒 E-commerce Performance Dashboard — {TEAM_NAME}")
st.caption(
    "For the **e-commerce manager**: if a key market's weekly revenue falls below its "
    "4-week average, shift marketing budget into that market."
)

# ---- filters the decision-maker actually uses ----
top_markets = df.groupby("Country")["Revenue"].sum().nlargest(6).index.tolist()
with st.sidebar:
    st.header("Filters")
    selected_countries = st.multiselect(
        "Country", options=sorted(df["Country"].unique()), default=top_markets
    )
    min_d, max_d = df["InvoiceDate"].min().date(), df["InvoiceDate"].max().date()
    date_range = st.date_input("Date range", value=(min_d, max_d))

# apply filters
if selected_countries:
    df = df[df["Country"].isin(selected_countries)]
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = date_range
    df = df[(df["InvoiceDate"].dt.date >= start) & (df["InvoiceDate"].dt.date <= end)]

# ---- headline KPIs (top: "is anything wrong right now?") ----
total_revenue = df["Revenue"].sum()
n_orders = df["InvoiceNo"].nunique()
aov = total_revenue / n_orders if n_orders else 0.0

c1, c2, c3 = st.columns(3)
c1.metric("Total revenue", f"£{total_revenue:,.0f}")
c2.metric("Orders", f"{n_orders:,}")
c3.metric("Average order value", f"£{aov:,.0f}")

st.markdown("---")

# ---- supporting charts (middle: explain why a number moved) ----
left, right = st.columns(2)

with left:
    st.subheader("Weekly revenue")
    weekly = (
        df.groupby("Week")["Revenue"].sum().reset_index()
    )
    fig_trend = px.line(
        weekly, x="Week", y="Revenue",
        title="Revenue by week — is it trending up or down?",
    )
    fig_trend.update_layout(yaxis_title="Revenue (£)", xaxis_title="")
    st.plotly_chart(fig_trend, use_container_width=True)

with right:
    st.subheader("Revenue by market")
    by_country = (
        df.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
        .head(10).reset_index()
    )
    fig_country = px.bar(
        by_country, x="Revenue", y="Country", orientation="h",
        title="Top markets — where the money comes from",
    )
    fig_country.update_layout(yaxis_title="", xaxis_title="Revenue (£)")
    st.plotly_chart(fig_country, use_container_width=True)

# ---- data period + refresh frequency line (Step 4) ----
st.markdown("---")
st.caption(f"**Data:** {DATA_PERIOD}.  **{REFRESH_NOTE}**  "
           "Cancellations, returns, and £0 items are excluded from revenue.")
