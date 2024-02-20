import numpy as np
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
    df = pd.DataFrame(normalized_coordinates, columns=['1st Dimension', '2nd Dimension', '3rd Dimension', '4th Dimension', '5th Dimension'])
    df['Category'] = coordinates_labels

    fig = px.parallel_coordinates(df.drop('Category', axis=1), color=df["Category"], color_continuous_scale=cluster_colors)
    fig.update_layout(coloraxis_showscale=False) 
    fig.update_layout(margin=dict(l=30, r=30, b=0, t=100))
    fig.update_layout(title="Parallel Coordinates of Embeddings")
    st.plotly_chart(fig,use_container_width=True)


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
