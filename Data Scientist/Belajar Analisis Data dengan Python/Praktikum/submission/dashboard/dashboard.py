import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set the style for seaborn
sns.set(style='dark')

# Function Definitions
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")['order_item_id'].sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bystate_df

def plot_product_sales(product_sales):
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(16, 6))
    product_sales.head(5).sort_values(ascending=True).plot(kind='barh', ax=ax0)
    ax0.set_title('Top 5 Best Performing Product Categories')
    ax0.set_xlabel('Number of Orders')
    ax0.set_ylabel('Product Category')
    product_sales.tail(5).sort_values(ascending=True).plot(kind='barh', ax=ax1)
    ax1.set_title('Worst 5 Performing Product Categories')
    ax1.set_xlabel('Number of Orders')
    ax1.set_ylabel('Product Category')
    plt.tight_layout()
    return fig

def plot_payment_types(customer_payment_groups):
    fig, ax = plt.subplots(figsize=(10, 6))
    customer_payment_groups.sort_values().plot(kind='barh', ax=ax, color="#90CAF9")
    ax.set_title('Unique Customers by Payment Type')
    ax.set_xlabel('Number of Unique Customers')
    ax.set_ylabel('Payment Type')
    plt.tight_layout()
    return fig

def plot_order_status(customer_order_status_groups):
    fig, ax = plt.subplots(figsize=(10, 6))
    customer_order_status_groups.sort_values().plot(kind='barh', ax=ax, color="#90CAF9")
    ax.set_title('Unique Customers by Order Status')
    ax.set_xlabel('Number of Unique Customers')
    ax.set_ylabel('Order Status')
    plt.tight_layout()
    return fig

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df    

# Load Data
all_df = pd.read_csv("all_data.csv")

# Convert datetime columns
datetime_columns = ["order_purchase_timestamp", "order_delivered_carrier_date"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

# Streamlit Sidebar
with st.sidebar:
    st.image("logo.jpg", width=100)
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter main DataFrame
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                  (all_df["order_purchase_timestamp"] <= str(end_date))]

# Data Analysis
daily_orders_df = create_daily_orders_df(main_df)
rfm_df = create_rfm_df(main_df)

# Product Sales Analysis
product_sales = main_df.groupby('product_category_name_english')['order_id'].count().sort_values(ascending=False)
most_sold_product = product_sales.idxmax()
most_sold_count = product_sales.max()
least_sold_product = product_sales.idxmin()
least_sold_count = product_sales.min()

# Dashboard Structure
st.header('E-Commerce Public Dataset Analysis')

# Daily Orders Purchased
st.subheader('Daily Orders Purchased')
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_purchase_timestamp"], daily_orders_df["order_count"], marker='o', linewidth=2, color="#90CAF9")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

# Product Sales Analysis
st.subheader('Product Sales Analysis')
product_sales_fig = plot_product_sales(product_sales)
st.pyplot(product_sales_fig)

# Customer Payment Analysis
st.subheader('Customer Payment Analysis')
customer_payment_groups = main_df.groupby('payment_type')['customer_unique_id'].nunique()
st.pyplot(plot_payment_types(customer_payment_groups))

# Customer Order Status Analysis
st.subheader('Customer Order Status Analysis')
customer_order_status_groups = main_df.groupby('order_status')['customer_unique_id'].nunique()
st.pyplot(plot_order_status(customer_order_status_groups))

# Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_monetary)

# RFM Analysis Plot
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis='x', labelsize=15, rotation=90)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15, rotation=90)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15, rotation=90)

plt.tight_layout()
st.pyplot(fig)