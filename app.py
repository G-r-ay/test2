import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.express as px

# Page Configuration
st.set_page_config(layout="wide")
st.sidebar.header("📊 Dashboard Controls")
st.title("Operational Insights")
st.text("""This dashboard provides metrics and insights on data processed within the Tempo application for cybersecurity.""")

# Sidebar Date Control
date_preset = st.sidebar.selectbox(
    "Date Preset",
    ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"]
)

today_date = datetime.now().date()
two_months_behind_today = today_date - timedelta(days=59)


def generate_sample_data():
    ingestion_times = pd.date_range(start=two_months_behind_today, end=today_date, freq='h').repeat(4)
    return pd.DataFrame({
        "ingestion_time": ingestion_times,
        "anchor_device": np.random.choice(["Workstation", "Webserver", "Ubuntu"], size=len(ingestion_times)),
        "n_datapoints": np.random.randint(50, 1200, size=len(ingestion_times)),
        "ingestion_style": np.random.choice(["static", "automated"], size=len(ingestion_times)),
        "anomaly_count": np.random.randint(0, 10, size=len(ingestion_times))
    })

# Data Processing Functions
def process_daily_metrics(df, style=None):
    if style:
        df = df[df['ingestion_style'] == style]
    
    daily_data = df.groupby(df['ingestion_time'].dt.date).agg({
        'n_datapoints': 'sum',
        'anomaly_count': 'sum'
    }).reset_index()
    
    daily_data.columns = ['date', 'total_datapoints', 'total_anomalies']
    return daily_data

def process_device_metrics(df, style=None):
    if style:
        df = df[df['ingestion_style'] == style]
    
    return df.groupby('anchor_device')['n_datapoints'].sum().to_dict()



# Load and Process Data
activity_data = generate_sample_data()

# Create sample data for references and streams DataFrames
references_data = pd.DataFrame({
    "reference_name": [f"Reference {i}" for i in range(1, 9)],
    "status": np.random.choice(["Assigned", "Unassigned"], size=8),
    "created_at": pd.date_range(start=today_date - timedelta(days=30), periods=8, freq='D')
})

streams_data = pd.DataFrame({
    "stream_name": [f"Stream {i}" for i in range(1, 6)],
    "status": np.random.choice(["Active", "Inactive"], size=5),
    "last_updated": pd.date_range(start=today_date - timedelta(days=10), periods=5, freq='D')
})

# Convert to DataFrames similar to the expected output
references_df = references_data
streams_df = streams_data


model_info = pd.DataFrame({
    "modeltype": [f"Function {i}" for i in range(1, 11)],
    "model_function": np.random.choice(["Type A", "Type B", "Type C"], size=10),
    "creation_time": pd.date_range(start=datetime.now() - timedelta(days=30), periods=10, freq='D'),
    "version": np.random.randint(1, 5, size=10)
})

model_info.columns = model_info.columns.str.lower()

highest_model_versions = model_info.loc[model_info.groupby('model_function')['version'].idxmax()]

date_range = (datetime.now() - timedelta(days=7), datetime.now())

if date_preset == "Custom Range":
    min_date = activity_data['ingestion_time'].min().date()
    max_date = activity_data['ingestion_time'].max().date()   # Get the minimum date from the dataframe
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(datetime.now() - timedelta(days=7), datetime.now()),
        min_value=min_date,  # Set the minimum date for the date input
        max_value=max_date,
        key="date_range"
    )
else:
    end_date = datetime.now()
    if date_preset == "Last 24 Hours":
        start_date = end_date - timedelta(days=1)
    elif date_preset == "Last 7 Days":
        start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=30)
    date_range = (start_date.date(), end_date.date())

# Data Generation
try:
    activity_data = activity_data[
        (activity_data['ingestion_time'].dt.date >= date_range[0]) & 
        (activity_data['ingestion_time'].dt.date <= date_range[1])
    ]
except IndexError as e:
    st.error("Date range doesn't have enough elements",icon="🚨")

# Separate data by ingestion style
automated_data = activity_data[activity_data['ingestion_style'] == 'automated']
static_data = activity_data[activity_data['ingestion_style'] == 'static']

# Process metrics
total_metrics = {
    'total_logs': activity_data['n_datapoints'].sum(),
    'automated_logs': automated_data['n_datapoints'].sum(),
    'static_logs': static_data['n_datapoints'].sum(),
    'total_anomalies': automated_data['anomaly_count'].sum()
}

# Process daily metrics
daily_metrics = {
    'overall': process_daily_metrics(activity_data),
    'automated': process_daily_metrics(activity_data, 'automated'),
    'static': process_daily_metrics(activity_data, 'static')
}

# Process device metrics
device_metrics = {
    'overall': process_device_metrics(activity_data),
    'automated': process_device_metrics(activity_data, 'automated'),
    'static': process_device_metrics(activity_data, 'static')
}

# Helper function for creating visualizations
def create_stacked_bar_chart(df, style_name):
    daily_device_logs = df.groupby([df['ingestion_time'].dt.date, 'anchor_device'])['n_datapoints'].sum().unstack(fill_value=0)
    
    fig = go.Figure(data=[
        go.Bar(name=device, x=daily_device_logs.index, y=daily_device_logs[device])
        for device in daily_device_logs.columns
    ])
    
    fig.update_layout(
        title=f'Daily Data Points by Device - {style_name}',
        xaxis_title='Date',
        yaxis_title='Data Points',
        barmode='stack'
    )
    return fig

def create_pie_chart(df, title):
    anomaly_count = df['anomaly_count'].sum()
    normal_count = df['n_datapoints'].sum() - anomaly_count
    
    data = pd.DataFrame({
        'Category': ['Anomalies', 'Normal Logs'],
        'Count': [anomaly_count, normal_count]
    })
    
    return px.pie(data, names='Category', values='Count', title=title)

def create_line_plot(df):
    daily_device_logs = df.groupby([df['ingestion_time'].dt.date, 'anchor_device'])['n_datapoints'].sum().reset_index()

    fig_line = go.Figure()
    for device in daily_device_logs['anchor_device'].unique():
        device_logs = daily_device_logs[daily_device_logs['anchor_device'] == device]
        fig_line.add_trace(go.Scatter(x=device_logs['ingestion_time'], y=device_logs['n_datapoints'], mode='lines', name=device))

    fig_line.update_layout(
        title='Daily Data Points Trend by Anchor Device',
        xaxis_title='Date',
        yaxis_title='Number of Data Points',
        legend_title='Anchor Device'
    )
    return fig_line


# Display Metrics
st.markdown("### 📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

recent_date = daily_metrics['overall']['date'].max()

recent_metrics = {
    'total': daily_metrics['overall'][daily_metrics['overall']['date'] == recent_date]['total_datapoints'].values[0] if len(daily_metrics['overall'][daily_metrics['overall']['date'] == recent_date]) > 0 else 0,
    'automated': daily_metrics['automated'][daily_metrics['automated']['date'] == recent_date]['total_datapoints'].values[0] if len(daily_metrics['automated'][daily_metrics['automated']['date'] == recent_date]) > 0 else 0,
    'static': daily_metrics['static'][daily_metrics['static']['date'] == recent_date]['total_datapoints'].values[0] if len(daily_metrics['static'][daily_metrics['static']['date'] == recent_date]) > 0 else 0,
    'anomalies': daily_metrics['automated'][daily_metrics['automated']['date'] == recent_date]['total_anomalies'].values[0] if len(daily_metrics['automated'][daily_metrics['automated']['date'] == recent_date]) > 0 else 0
}

col1.metric("Total Data Points", f"{total_metrics['total_logs']:,.0f}", f"{recent_metrics['total']:,.0f}")
col2.metric("Automated Data Points", f"{total_metrics['automated_logs']:,.0f}", f"{recent_metrics['automated']:,.0f}")
col3.metric("Static Data Points", f"{total_metrics['static_logs']:,.0f}", f"{recent_metrics['static']:,.0f}")
col4.metric("Anomalies (Automated)", f"{total_metrics['total_anomalies']:,.0f}", f"{recent_metrics['anomalies']:,.0f}")

# Create tabs
overall_tab, automated_tab, static_tab, control = st.tabs(["📈 Overall", "⚙️ Automated", "📊 Static", "🛠️ Infra"])

with overall_tab:
    # Overall visualizations
    st.plotly_chart(create_stacked_bar_chart(activity_data, "Overall"), use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    devices = ["Workstation", "Webserver", "Ubuntu"]
    for i, device in enumerate(devices):
        count = device_metrics['overall'].get(device, 0)  # Get count or default to 0
        if i % 3 == 0:
            with col1:
                st.metric(f"{device} Data Points", f"{count:,.0f}")
        elif i % 3 == 1:
            with col2:
                st.metric(f"{device} Data Points", f"{count:,.0f}")
        else:
            with col3:  
                st.metric(f"{device} Data Points", f"{count:,.0f}")



    col1, col2 = st.columns([0.65, 0.35])
    with col1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=daily_metrics['static']['date'],
            y=daily_metrics['static']['total_datapoints'],
            name='Static Data Points'
        ))
        fig_trend.add_trace(go.Scatter(
            x=daily_metrics['automated']['date'],
            y=daily_metrics['automated']['total_datapoints'],
            name='Automated Data Points'
        ))
        fig_trend.update_layout(title='Daily Data Points Trend by Ingestion Style')
        st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        style_distribution = pd.DataFrame({
            'Style': ['Static', 'Automated'],
            'Count': [total_metrics['static_logs'], total_metrics['automated_logs']]
        })
        fig_pie = px.pie(style_distribution, names='Style', values='Count',
                        title='Distribution of Ingestion Styles')
        st.plotly_chart(fig_pie, use_container_width=True)

with automated_tab:
    st.plotly_chart(create_stacked_bar_chart(automated_data, "Automated"), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    for i, (device, count) in enumerate(device_metrics['automated'].items()):
        if i % 3 == 0:
            with col1:
                st.metric(f"{device} Data Points", f"{count:,.0f}")
        elif i % 3 == 1:
            with col2:
                st.metric(f"{device} Data Points", f"{count:,.0f}")
        else:
            with col3:
                st.metric(f"{device} Data Points", f"{count:,.0f}")

    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.plotly_chart(create_line_plot(automated_data), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_pie_chart(automated_data, "Automated Data - Anomalies Distribution"),
                       use_container_width=True)

        

with static_tab:
    st.plotly_chart(create_stacked_bar_chart(static_data, "Static"), use_container_width=True)

    col1, col2, col3 = st.columns(3)
    for i, (device, count) in enumerate(device_metrics['static'].items()):
        if i % 3 == 0:
            with col1:
                st.metric(f"{device} Data Points", f"{count:,.0f}")
        elif i % 3 == 1:
            with col2:
                st.metric(f"{device} Data Points", f"{count:,.0f}")
        else:
            with col3:
                st.metric(f"{device} Data Points", f"{count:,.0f}")

    with st.container():
        col1, col2 = st.columns([0.7, 0.3])
        
        with col1:
            st.plotly_chart(create_line_plot(static_data), use_container_width=True)

        with col2:
            st.plotly_chart(create_pie_chart(static_data, "Static Data Distribution"),
                        use_container_width=True)




with control:
    st.subheader("Models")
    if not highest_model_versions.empty:
        st.write("Model Information:")
        st.dataframe(highest_model_versions, use_container_width=True)
    else:
        st.warning("Please initialize the base models by running ```CALL MANAGEMENT.CREATE_RESOURCES()```")
    st.subheader("Streams")
    if not streams_df.empty:
        st.write("Active Streams:")
        st.dataframe(streams_df, use_container_width=True)
    else:
        st.text("No active streams.")
