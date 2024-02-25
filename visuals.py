import numpy as np
import time
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sentence_generator import augmented_sentences
from embedders import umap_embeddings_3d,cluster_labels_3d,umap_embeddings_2d,cluster_labels_2d,normalized_coordinates,coordinates_labels
st.set_page_config(layout='wide')
coordinate_colors = ['#0E1117','#FF6978','#340068','#F9A03F','#0E1117']
cluster_colors = ['#FF6978','#340068','#F9A03F']
st.title("Model Embeddings Visualizations")


def update_dimension_subset(start_dim, end_dim, df):
    subset_df = df.iloc[:, start_dim:end_dim]
    return subset_df

with st.container():
    embedding_traces = []
    for i, cluster_label in enumerate(np.unique(cluster_labels_3d)):
        cluster_points = umap_embeddings_3d[cluster_labels_3d == cluster_label]
        cluster_text = [augmented_sentences[j] for j, label in enumerate(cluster_labels_3d) if label == cluster_label]
        trace = go.Scatter3d(
            x=cluster_points[:, 0],
            y=cluster_points[:, 1],
            z=cluster_points[:, 2],
            mode='markers',
            marker=dict(
                size=5,
                color=cluster_colors[i],
                opacity=0.8
            ),
            text=cluster_text,
            hoverinfo='text',
            name=f'Cluster {cluster_label}' 
        )
        embedding_traces.append(trace)

    embedding_figure = go.Figure(data=embedding_traces)

    embedding_figure.update_traces(marker_size=5)

    embedding_figure.update_layout(margin=dict(l=0, r=0, b=0, t=30))
    camera = dict(
        up=dict(x=1, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=0, y=0, z=1.25)
    )
    embedding_figure.update_layout(
        title="3D Visualization of Sequence Embeddings",
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False),
            zaxis=dict(showticklabels=False)
    )
    )
    embedding_figure.update_layout(scene_camera=camera)

    st.plotly_chart(embedding_figure, use_container_width=True)

#----------------------------------------------------------------------------------------------------
st.write("<br>", unsafe_allow_html=True)
#----------------------------------------------------------------------------------------------------

with st.container():
    df = pd.DataFrame(normalized_coordinates, columns=[f'{i+1}st Dimension' for i in range(normalized_coordinates.shape[1])])
    df['Category'] = coordinates_labels


    if 'start_dim' not in st.session_state:
        st.session_state.start_dim =  1
    if 'end_dim' not in st.session_state:
        st.session_state.end_dim =  5

    max_dimensions = len(df.columns) -  1
    slider_value = st.slider('Select Start Dimension',  1, max_dimensions)
    st.session_state.start_dim = slider_value
    st.session_state.end_dim = st.session_state.start_dim +  4

    fig = px.parallel_coordinates(
        df.iloc[:, st.session_state.start_dim-1:st.session_state.end_dim].join(df['Category'].rename('Category_Label')),  
        color='Category_Label',  
        color_continuous_scale='viridis'
    )

    fig.update_layout(
        coloraxis_showscale=False,  
        margin=dict(l=30, r=30, b=0, t=100),
        title="Parallel Coordinates of Embeddings"
    )

    chart = st.plotly_chart(fig, use_container_width=True)

    if st.session_state.end_dim > len(df.columns)-1:
        st.session_state.end_dim = len(df.columns)
        subset_df = update_dimension_subset(st.session_state.start_dim-1, st.session_state.end_dim, df)
        fig.data[0]['dimensions'] = [dict(range=[min(subset_df.iloc[:, i]), max(subset_df.iloc[:, i])],  
        label=subset_df.columns[i], values=subset_df.iloc[:, i]) for i in range(len(subset_df.columns))]
        chart.plotly_chart(fig, use_container_width=True)


    auto_update = st.checkbox('Continuous Data Flow')
    if auto_update:
        start_time = time.time()
        while True:
            current_time = time.time()
            if current_time - start_time >= 1:
                start_time = current_time
                st.session_state.start_dim += 1
                st.session_state.end_dim += 1
                if st.session_state.end_dim > len(df.columns):
                    st.session_state.start_dim = 0
                    st.session_state.end_dim = 5
                elif st.session_state.start_dim >= len(df.columns):
                    st.session_state.start_dim = 0
                    st.session_state.end_dim = min(5, len(df.columns))
                
                subset_df = update_dimension_subset(st.session_state.start_dim, st.session_state.end_dim, df)
                fig.data[0]['dimensions'] = [dict(range=[min(subset_df.iloc[:, i]), max(subset_df.iloc[:, i])], label=subset_df.columns[i], values=subset_df.iloc[:, i]) for i in range(len(subset_df.columns))]
                chart.plotly_chart(fig, use_container_width=True)
            else:
                time.sleep(0.05)
    
#----------------------------------------------------------------------------------------------------
st.write("<br>", unsafe_allow_html=True)
#----------------------------------------------------------------------------------------------------
with st.container():
    fig = go.Figure(data=go.Scatter(
        x=umap_embeddings_2d[:, 0],
        y=umap_embeddings_2d[:, 1],
        mode='markers',
        marker=dict(
            color=[cluster_colors[label - 1] for label in cluster_labels_2d],
            size=10,
            opacity=0.7
        ),
        text=augmented_sentences,
        hoverinfo='text'
    ))
    fig.update_layout(margin=dict(l=30, r=30, b=0, t=110))
    fig.update_layout(
        title='Scatter Plot Of Embeddings(2D)',
        xaxis_title='X',
        yaxis_title='Y',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
