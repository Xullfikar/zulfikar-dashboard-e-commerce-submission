import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")


# create_daily_orders_df()
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_approved_at").agg(
        {"order_id": "nunique", "price": "sum"}
    )
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(
        columns={"order_id": "order_count", "price": "revenue"}, inplace=True
    )

    return daily_orders_df


# create_sum_review_score_df()
def create_sum_review_score_df(df):
    sum_review_score_filtered = df[df["review_id"] != "no_review"]
    sum_review_score_df = (
        sum_review_score_filtered.groupby(by="product_id")
        .review_score.sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    return sum_review_score_df


# create_sum_order_items_df()
def create_sum_order_items_df(df):
    sum_order_items_df = (
        df.groupby("product_id")
        .order_item_id.count()
        .sort_values(ascending=False)
        .reset_index()
    )
    return sum_order_items_df


# create_bystate_df(df)
def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    return bystate_df


#
def create_sum_review_score_seller_df(df):
    sum_review_score_filtered = df[df["review_id"] != "no_review"]
    sum_review_score_seller_df = (
        sum_review_score_filtered.groupby(by="seller_id")
        .review_score.sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    return sum_review_score_seller_df


# create_rfm_df()
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg(
        {"order_approved_at": "max", "order_id": "nunique", "price": "sum"}
    )
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


all_df = pd.read_csv("./main_data.csv")

datetime_columns = ["order_approved_at"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

format_waktu = "ISO8601"
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column], format=format_waktu)

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max() + pd.Timedelta(days=1)

with st.sidebar:
    st.image("./andi_zulfikar.jpg")

    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = all_df[
    (all_df["order_approved_at"] >= str(start_date))
    & (all_df["order_approved_at"] <= str(end_date))
]

daily_orders_df = create_daily_orders_df(main_df)
sum_review_score_df = create_sum_review_score_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bystate_df = create_bystate_df(main_df)
sum_review_score_seller_df = create_sum_review_score_seller_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header("E-Commerce Public Dashboard :sparkles:")

# Daily orders
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "AUD ", locale="es_CO"
    )
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#450557",
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)

st.pyplot(fig)

# Produk dengan reviews score dan penjualan tertinggi
st.subheader("Produk dengan Reviews Score dan Penjualan Tertinggi")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#450557", "C7", "C7", "C7", "C7"]

sns.barplot(
    x="review_score",
    y="product_id",
    data=sum_review_score_df.head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Reviews Score", fontsize=30)
ax[0].set_title("Produk dengan Reviews Score Tertinggi", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=35)
ax[0].tick_params(axis="x", labelsize=30)

sns.barplot(
    x="order_item_id",
    y="product_id",
    data=sum_order_items_df.head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Total Penjualan", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk dengan Penjualan Tertinggi", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=35)
ax[1].tick_params(axis="x", labelsize=30)

st.pyplot(fig)

# Customer Demographics
st.subheader("Customer Demographics")
fig, ax = plt.subplots(figsize=(20, 10))
colors = "viridis"
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax,
)
ax.set_title("Jumlah Pelanggan berdasarkan Negara", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)
st.pyplot(fig)


# Seller dengan Review Tertinggi
st.subheader("Seller dengan Review Score Tertinggi")
fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#450557", "C7", "C7", "C7", "C7"]
sns.barplot(
    x="review_score",
    y="seller_id",
    data=sum_review_score_seller_df.sort_values(
        by="review_score", ascending=False
    ).head(5),
    palette=colors,
    ax=ax,
)
ax.set_title("Seller dengan Reviews Score Tertinggi", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)
st.pyplot(fig)

# Kostumer Terbaik berdasarkan RFM Parameters
st.subheader("Kostumer Terbaik berdasarkan RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Rata-Rata Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Rata-Rata Frequency", value=avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD ", locale="es_CO")
    st.metric("Rata-Rata Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#450557", "#450557", "#450557", "#450557", "#450557"]

sns.barplot(
    x="customer_id",
    y="recency",
    data=rfm_df.sort_values(by="recency", ascending=True).head(5),
    palette=colors,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=30)
ax[0].tick_params(axis="x", labelsize=35)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=90)

sns.barplot(
    y="frequency",
    x="customer_id",
    data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
    palette=colors,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=35)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=90)

sns.barplot(
    y="monetary",
    x="customer_id",
    data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
    palette=colors,
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis="y", labelsize=30)
ax[2].tick_params(axis="x", labelsize=35)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=90)

st.pyplot(fig)

st.caption("Created by Andi Zulfikar")
