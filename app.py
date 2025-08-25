import streamlit as st
import pandas as pd
import plotly.express as px

# Fixed Google Sheet URL (CSV export link)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1A-t_nWfPTvZJ2XMlXgu5KwGbJp_Eawmr6W-EuzPztks/export?format=csv"

# Set wide layout
st.set_page_config(layout="wide")

# Inject custom CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        header, footer, .stDeployButton {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def load_data(sheet_url):
    try:
        df = pd.read_csv(sheet_url, header=0, parse_dates=["Date"])
        df = df.sort_values("Date")
        df["Amount"] = pd.to_numeric(df["Amount (PKR)"], errors="coerce")
        df["Year"] = df["Date"].dt.year
        df["Month"] = df["Date"].dt.month_name()
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load data: {e}")
        return pd.DataFrame()

df = load_data(SHEET_URL)

if not df.empty:
    selected_year = st.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
    # selected_month = st.selectbox("Select Month", df[df["Year"] == selected_year]["Month"].unique())
    months_in_year = (
        df[df["Year"] == selected_year]
        .sort_values("Date")["Month"]
        .unique()
    )

    # Pick latest month as default
    latest_month = months_in_year[-1]

    selected_month = st.selectbox(
        "Select Month",
        months_in_year,
        index=len(months_in_year) - 1  # default to last (latest) month
)

    filtered_df = df[(df["Year"] == selected_year) & (df["Month"] == selected_month)]
    income_df = filtered_df[filtered_df["Type"] == "Income"]
    expense_df = filtered_df[filtered_df["Type"] == "Expense"]

    initial_investment = df[df["Type"] == "Initial"]["Amount"].sum()
    income_till_now = df[(df["Date"] <= filtered_df["Date"].max()) & (df["Type"] == "Income")]["Amount"].sum()
    expense_till_now = df[(df["Date"] <= filtered_df["Date"].max()) & (df["Type"] == "Expense")]["Amount"].sum()
    current_balance = initial_investment + income_till_now - expense_till_now

    # Title
    st.markdown("<h1 style='text-align: center;'>📊 Brainscraft Finance Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: gray;'>Finance Overview for {selected_month} {selected_year}</h3>", unsafe_allow_html=True)

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Initial Investment", f"{initial_investment:,.0f} PKR")
    col2.metric("💰 Income (till now)", f"{income_till_now:,.0f} PKR")
    col3.metric("💸 Expense (till now)", f"{expense_till_now:,.0f} PKR")
    col4.metric("🧮 Current Balance", f"{current_balance:,.0f} PKR")

    st.divider()

    # Charts Row 1
    st.subheader("📈 Cashflow & Summary")
    col5, col6 = st.columns(2)

    with col5:
        flow_data = filtered_df.copy()
        flow_data["Cumulative Balance"] = flow_data["Amount"].cumsum()
        fig_flow = px.line(flow_data, x="Date", y="Cumulative Balance", title="💹 Cumulative Cashflow")
        st.plotly_chart(fig_flow, use_container_width=True)

    with col6:
        summary_bar = px.bar(
            x=["Income", "Expense"],
            y=[income_df["Amount"].sum(), expense_df["Amount"].sum()],
            title="📊 Monthly Summary",
            labels={"x": "Type", "y": "Amount"},
            color=["Income", "Expense"]
        )
        st.plotly_chart(summary_bar, use_container_width=True)

    # Charts Row 2
    st.subheader("🔍 Breakdown by Category")
    col7, col8 = st.columns(2)

    with col7:
        expense_by_cat = expense_df.groupby("Category")["Amount"].sum().abs().reset_index()
        if not expense_by_cat.empty:
            fig_expense_cat = px.pie(expense_by_cat, names="Category", values="Amount", title="📉 Expenses by Category")
            st.plotly_chart(fig_expense_cat, use_container_width=True)
        else:
            st.info("No expenses recorded for this month.")

    with col8:
        income_by_cat = income_df.groupby("Category")["Amount"].sum().reset_index()
        if not income_by_cat.empty:
            fig_income_cat = px.pie(income_by_cat, names="Category", values="Amount", title="📈 Income by Category")
            st.plotly_chart(fig_income_cat, use_container_width=True)
        else:
            st.info("No income recorded for this month.")

    # Transaction Table
    st.subheader("📋 Transactions")
    st.dataframe(filtered_df[["Date", "Type", "Category", "Description", "Amount"]], use_container_width=True)

    # Footer
    st.markdown("""
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            text-align: center;
            color: gray;
            padding: 10px;
            background-color: white;
        }
        </style>
        <div class="footer">© 2025 All rights reserved by <strong>Brainscraft Technologies</strong>.</div>
    """, unsafe_allow_html=True)
else:
    st.warning("No data found in sheet.")
