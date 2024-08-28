import streamlit as st

# Basic information and plans
st.title("Snowflake Cost Estimator")

st.markdown("""
This tool allows you to estimate the cost of running your application on Snowflake based on your compute resources, storage needs, data transfer, and the Snowflake plan you choose.
""")

# Select Snowflake plan
st.header("Choose Your Snowflake Plan")
plan = st.selectbox("Snowflake Plan", ["Standard", "Enterprise", "Business Critical", "Virtual Private Snowflake (VPS)"])

# Input compute resources
st.header("Compute Resources")
num_warehouses = st.number_input("Number of Warehouses", min_value=1, value=1)
warehouse_size = st.selectbox("Warehouse Size", ["X-Small", "Small", "Medium", "Large", "X-Large", "2X-Large", "3X-Large", "4X-Large"])
hours_per_day = st.slider("Average Hours Per Day", 1, 24, 8)

# Advanced warehouse usage options
st.header("Advanced Warehouse Usage Options")
auto_suspend = st.checkbox("Use Auto-Suspend", value=True)
auto_resume = st.checkbox("Use Auto-Resume", value=True)

# Input storage resources
st.header("Storage Costs")
storage_tb = st.number_input("Data Stored (TB)", min_value=0.1, value=1.0)
storage_type = st.selectbox("Storage Type", ["Standard", "Time Travel", "Fail-safe"])

# Input data transfer
st.header("Data Transfer Costs")
data_transfer_tb = st.number_input("Data Transfer (TB)", min_value=0.1, value=1.0)
transfer_type = st.selectbox("Transfer Type", ["Intra-Region", "Inter-Region", "Inter-Cloud"])

# Cost per credit for each plan (example values, adjust as needed)
cost_per_credit = {
    "Standard": 2.0,
    "Enterprise": 2.5,
    "Business Critical": 3.0,
    "Virtual Private Snowflake (VPS)": 4.0,
}

# Compute resources to credits conversion (example conversion rates)
credits_per_hour = {
    "X-Small": 1,
    "Small": 2,
    "Medium": 4,
    "Large": 8,
    "X-Large": 16,
    "2X-Large": 32,
    "3X-Large": 64,
    "4X-Large": 128,
}

# Storage costs (example values)
storage_cost_per_tb = {
    "Standard": 23,
    "Time Travel": 46,
    "Fail-safe": 92,
}

# Data transfer costs (example values)
transfer_cost_per_tb = {
    "Intra-Region": 0.00,  # Free within the same region
    "Inter-Region": 9.0,
    "Inter-Cloud": 20.0,
}

# Calculate estimated costs
selected_plan_cost_per_credit = cost_per_credit[plan]
selected_warehouse_credits_per_hour = credits_per_hour[warehouse_size]
estimated_daily_credits = num_warehouses * selected_warehouse_credits_per_hour * hours_per_day
estimated_monthly_credits = estimated_daily_credits * 30  # Assuming 30 days in a month
estimated_monthly_compute_cost = estimated_monthly_credits * selected_plan_cost_per_credit

# Storage cost calculation
estimated_storage_cost = storage_tb * storage_cost_per_tb[storage_type]

# Data transfer cost calculation
estimated_transfer_cost = data_transfer_tb * transfer_cost_per_tb[transfer_type]

# Total estimated cost
total_estimated_monthly_cost = estimated_monthly_compute_cost + estimated_storage_cost + estimated_transfer_cost

# Display the estimate
st.header("Estimated Cost")
st.write(f"**Plan:** {plan}")
st.write(f"**Warehouse Size:** {warehouse_size}")
st.write(f"**Estimated Monthly Compute Cost:** ${estimated_monthly_compute_cost:,.2f}")
st.write(f"**Estimated Monthly Storage Cost:** ${estimated_storage_cost:,.2f}")
st.write(f"**Estimated Monthly Data Transfer Cost:** ${estimated_transfer_cost:,.2f}")
st.write(f"**Total Estimated Monthly Cost:** ${total_estimated_monthly_cost:,.2f}")

st.markdown("""
*Note: This is a guesstimate. Actual costs may vary based on other factors like data storage, data transfer, and additional services.
""")

if st.checkbox("Show detailed calculation"):
    st.write(f"Cost per credit for selected plan: ${selected_plan_cost_per_credit:,.2f}")
    st.write(f"Credits per hour for selected warehouse size: {selected_warehouse_credits_per_hour} credits")
    st.write(f"Estimated daily credits: {estimated_daily_credits:,.2f} credits")
    st.write(f"Estimated monthly credits: {estimated_monthly_credits:,.2f} credits")
    st.write(f"Storage cost per TB for selected type: ${storage_cost_per_tb[storage_type]:,.2f}")
    st.write(f"Data transfer cost per TB for selected type: ${transfer_cost_per_tb[transfer_type]:,.2f}")
