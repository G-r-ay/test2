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
warehouse_size = st.selectbox("Warehouse Size", ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"])
warehouse_type = st.radio("Warehouse Type", ["Standard", "Snowpark-Optimized"])
hours_per_day = st.slider("Average Hours Per Day", 1, 24, 8)

# Cloud Services Cost
cloud_services_usage = st.checkbox("Include Cloud Services Cost", value=True)

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
transfer_region = st.selectbox("Data Transfer Region", ["Same Region", "Different Region, Same Continent", "Different Continent"])
transfer_type = st.selectbox("Transfer Type", ["Intra-Region", "Inter-Region", "Inter-Cloud"])

# Cost per credit for each plan (from PDF data, adjust as needed)
cost_per_credit = {
    "Standard": 2.0,
    "Enterprise": 2.5,
    "Business Critical": 3.0,
    "Virtual Private Snowflake (VPS)": 4.0,
}

# Compute resources to credits conversion based on PDF
credits_per_hour = {
    "Standard": {"XS": 1, "S": 2, "M": 4, "L": 8, "XL": 16, "2XL": 32, "3XL": 64, "4XL": 128},
    "Snowpark-Optimized": {"XS": None, "S": None, "M": 6, "L": 12, "XL": 24, "2XL": 48, "3XL": 96, "4XL": 192}
}

# Storage costs (from PDF)
storage_cost_per_tb = {
    "Standard": 23,
    "Time Travel": 46,
    "Fail-safe": 92,
}

# Data transfer costs (from PDF)
data_transfer_cost_per_tb = {
    "Same Region": 0.00,
    "Different Region, Same Continent": 10.00,
    "Different Continent": 80.00,
    "Inter-Cloud": 150.00,
}

# Cloud Services Cost (from PDF)
cloud_services_credit_per_hour = 4.4

# Calculate estimated costs
selected_plan_cost_per_credit = cost_per_credit[plan]
selected_warehouse_credits_per_hour = credits_per_hour[warehouse_type][warehouse_size]
estimated_daily_credits = num_warehouses * selected_warehouse_credits_per_hour * hours_per_day
estimated_monthly_credits = estimated_daily_credits * 30  # Assuming 30 days in a month
estimated_monthly_compute_cost = estimated_monthly_credits * selected_plan_cost_per_credit

# Cloud services cost
estimated_cloud_services_cost = 0
if cloud_services_usage:
    estimated_cloud_services_cost = cloud_services_credit_per_hour * 30 * 24  # Assuming cloud services run 24/7

# Storage cost calculation
estimated_storage_cost = storage_tb * storage_cost_per_tb[storage_type]

# Data transfer cost calculation
estimated_transfer_cost = data_transfer_tb * data_transfer_cost_per_tb[transfer_region]

# Total estimated cost
total_estimated_monthly_cost = estimated_monthly_compute_cost + estimated_storage_cost + estimated_transfer_cost + estimated_cloud_services_cost

# Display the estimate
st.header("Estimated Cost")
st.write(f"**Plan:** {plan}")
st.write(f"**Warehouse Size:** {warehouse_size}")
st.write(f"**Warehouse Type:** {warehouse_type}")
st.write(f"**Estimated Monthly Compute Cost:** ${estimated_monthly_compute_cost:,.2f}")
st.write(f"**Estimated Monthly Storage Cost:** ${estimated_storage_cost:,.2f}")
st.write(f"**Estimated Monthly Data Transfer Cost:** ${estimated_transfer_cost:,.2f}")
if cloud_services_usage:
    st.write(f"**Estimated Monthly Cloud Services Cost:** ${estimated_cloud_services_cost:,.2f}")
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
    st.write(f"Data transfer cost per TB for selected region: ${data_transfer_cost_per_tb[transfer_region]:,.2f}")
    if cloud_services_usage:
        st.write(f"Cloud Services cost per hour: ${cloud_services_credit_per_hour:,.2f} credits")
