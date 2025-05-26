
# sheet_url = "https://docs.google.com/spreadsheets/d/1KzLZvH1IaKOqLWQmDA2HK68S_NXZwxgIaHrO7RwtO7w/export?format=csv"
import streamlit as st
import pandas as pd
import plotly.express as px

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

# Sidebar: Input Sheet URL
st.sidebar.markdown("### 🔗 Google Sheet URL")
user_sheet_url = st.sidebar.text_input(
    "Paste your Google Sheet URL below",
    placeholder="https://docs.google.com/spreadsheets/d/xxxxxxx/edit#gid=0"
)

def convert_to_csv_url(gsheet_url):
    try:
        if "edit?usp=sharing" in gsheet_url:
            sheet_id = gsheet_url.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        elif "export?format=csv" in gsheet_url:
            return gsheet_url
        else:
            return None
    except:
        return None

sheet_url = convert_to_csv_url(user_sheet_url)

@st.cache_data(ttl=60)
def load_data(sheet_url):
    if sheet_url is None:
        return pd.DataFrame()
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

if sheet_url:
    df = load_data(sheet_url)

    if not df.empty:
        selected_year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique(), reverse=True))
        selected_month = st.sidebar.selectbox("Select Month", df[df["Year"] == selected_year]["Month"].unique())

        filtered_df = df[(df["Year"] == selected_year) & (df["Month"] == selected_month)]
        income_df = filtered_df[filtered_df["Type"] == "Income"]
        expense_df = filtered_df[filtered_df["Type"] == "Expense"]

        initial_investment = df[df["Type"] == "Initial"]["Amount"].sum()
        income_till_now = df[(df["Date"] <= filtered_df["Date"].max()) & (df["Type"] == "Income")]["Amount"].sum()
        expense_till_now = df[(df["Date"] <= filtered_df["Date"].max()) & (df["Type"] == "Expense")]["Amount"].sum()
        current_balance = initial_investment + income_till_now - expense_till_now

        # Title
        st.markdown("<h1 style='text-align: center;'>📊 Brainscraft Finance Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: gray;'>Finance Overview for {selected_month} {selected_year}</h3>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

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


        st.markdown("<br>", unsafe_allow_html=True)
        # Transaction Table
        st.subheader("📋 Transactions")
        st.dataframe(filtered_df[["Date", "Type", "Category", "Description", "Amount"]], use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
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
else:
    st.warning("Please paste a valid Google Sheet URL in the sidebar.")
