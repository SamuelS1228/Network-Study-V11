import streamlit as st
import pandas as pd
from optimization import optimize
from visualization import plot_network, summary

st.set_page_config(page_title="Warehouse Cost Optimizer", page_icon="⚙️", layout="wide")
st.title("Warehouse Network Cost Optimizer")

st.markdown("Upload a CSV with **Latitude**, **Longitude**, **DemandLbs** columns.")

uploaded = st.file_uploader("Upload store demand file", type=['csv'])

with st.sidebar:
    st.header("Cost Parameters")
    cost_per_lb_mile = st.number_input("Transportation cost $ per lb‑mile", value=0.02, format="%.10f")
    fixed_cost = st.number_input("Fixed cost per warehouse ($/yr)", value=250000.0, step=50000.0, format="%.2f")
    sqft_per_lb = st.number_input("Warehouse sqft per lb", value=0.02, format="%.10f")
    cost_per_sqft = st.number_input("Variable cost $ per sqft per yr", value=6.0, format="%.10f")
    st.markdown("---")
    auto_k = st.checkbox("Optimize number of warehouses", value=True)
    if auto_k:
        k_min,k_max = st.slider("K range",1,10,(2,5))
    else:
        k_fixed = st.number_input("Number of warehouses",1,10,3,1)

if uploaded:
    df = pd.read_csv(uploaded)

    # ── Truncate to at most 1 000 stores ─────────────────────────────
    if len(df) > 1000:
        st.warning(
            "File contains more than 1,000 stores; only the first 1,000 will be used."
        )
        df = df.iloc[:1000]
    # ─────────────────────────────────────────────────────────────────

    required={'Latitude','Longitude','DemandLbs'}
    if not required.issubset(df.columns):
        st.error(f"CSV must have columns {', '.join(required)}")
        st.stop()
    if auto_k:
        result = optimize(df, range(k_min, k_max+1), cost_per_lb_mile, sqft_per_lb, cost_per_sqft, fixed_cost)
        st.success(f"Optimal k = {result['k']}")
    else:
        result = optimize(df, [int(k_fixed)], cost_per_lb_mile, sqft_per_lb, cost_per_sqft, fixed_cost)
    plot_network(result['assigned_df'], result['centers'])
    summary(result['assigned_df'], result['total_cost'], result['trans_cost'], result['wh_cost'], result['centers'], result['demand_per_wh'], sqft_per_lb)
