# E-commerce Performance Dashboard

A Streamlit dashboard for a UK online retailer's **e-commerce manager**, built on the
[Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail) (also on Kaggle).

---

## Step 1 — The dataset and the decision-maker

**Dataset:** [Online Retail (UCI Machine Learning Repository, dataset 352)](https://archive.ics.uci.edu/dataset/352/online+retail),
a transnational dataset of all transactions for a UK-based, non-store online retailer between
**1 Dec 2010 and 9 Dec 2011**. The company sells unique all-occasion gifts, and many of its customers
are wholesalers. Each row is **one line item on one invoice**, with `InvoiceNo`, `StockCode`,
`Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, and `Country`.

It is **real data** (not synthetic). The full file is 541,909 rows (about 24 MB), so I sampled it down
to **100,000 rows** with `random_state=42` and committed the smaller CSV — the dashboard itself reads
`online_retail.csv`.

**Decision-maker:** the **e-commerce manager**, who owns weekly revenue across markets and decides
where to spend the marketing budget.

---

## Step 2 — Why a dashboard

1. **Who and how often:** the e-commerce manager, looking at it every **Monday morning**.
2. **The decision it supports:** *"If the manager sees a country's weekly revenue fall below its
   4-week average, they will shift marketing budget into that country."* The dashboard exists to make
   that comparison fast and visible.
3. **What they do today:** they export the transaction log to Excel, pivot it by hand, and rebuild the
   same weekly report every Monday — about half a day of work, and easy to get wrong. That is time not
   spent actually acting on the numbers.
4. **Why a dashboard, not a weekly email or a report:** the questions are the same every week
   ("how did each market do, and is anyone slipping?"), and the answer changes what the manager does
   *that same week*. A fixed email can't be filtered by country or zoomed into a date range; a
   dashboard can. It is not a one-off question, so it earns its place.

---

## Step 3 — What I showed, and what I cut

**Headline numbers (top, seen in five seconds):**
- **Total revenue** — the "is anything wrong?" number.
- **Orders** — how many invoices, to separate revenue growth from just higher prices.
- **Average order value** — because the manager also cares whether growth comes from more customers
  or bigger baskets.

**Supporting charts (middle, explain *why* a number moved):**
- **Weekly revenue trend** — shows *when* revenue rose or fell, which is what the 4-week comparison
  needs.
- **Revenue by market (top 10)** — shows *where* the money comes from, so the manager knows which
  countries to watch.

**Filters (only what the manager uses):**
- **Country** multi-select, defaulting to the top markets, because the decision is market-by-market.
- **Date range**, to zoom into a specific period.

**Order of the page:** headline metrics on top, then the two explanatory charts side by side, with
filters in the sidebar. Nothing below the fold except the data-period note.

**Two things I chose *not* to show, and why:**
1. **A customer-level table** (individual `CustomerID` transactions). It is the most tempting detail,
   but the manager acts on *markets*, not individual customers, and it would bury the trend that
   matters under thousands of rows.
2. **A product / StockCode breakdown.** Interesting in EDA, but the manager doesn't re-plan products
   weekly — marketing is decided per country. A product view would be a second dashboard, not this one.

**What could mislead the viewer, and how I handle it:**
- **Negative `Quantity` and invoices starting with "C" are cancellations/returns, not sales.** I
  exclude them from every metric so revenue is never inflated.
- **`UnitPrice` of 0** (freebies or data errors) is also excluded.
- **`CustomerID` is missing for about 25% of rows** (guest/wholesale orders). I keep those rows for
  revenue and order counts (they are real sales) but never show customer-level numbers, so the
  missing IDs can't mislead anyone.
- The chart titles and the data-period note state the date range so nobody reads 2010–2011 numbers as
  "today".

---

## Step 4 — Refresh frequency

1. **How often to refresh:** **nightly**. Transactions land in the system continuously, but the
   decision is weekly, so more frequent refreshes would add cost without changing any decision.
2. **How often to review:** **every Monday morning**, when the manager reallocates marketing budget.
   Refresh and review are deliberately different — the data updates nightly, the person acts weekly.
3. **What to track and what triggers action:** track **weekly revenue per country**. The alert is
   when a country's weekly revenue drops **more than 20% below its 4-week rolling average** — that is
   when the manager should pick up the phone and investigate (a campaign ended, a competitor moved,
   a checkout broke).
4. **What stale data costs:** if the dashboard were a week out of date, the manager would miss a
   market that has been slipping for a full week — losing orders to competitors before anyone notices.
   A day of staleness is tolerable; a week is not.

---

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Deployed on Streamlit Cloud with Python **3.14** under Advanced settings.
