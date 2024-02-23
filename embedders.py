import torch
import numpy as np
from umap import UMAP
from sentence_generator import augmented_sentences
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer


random_seed = 27
np.random.seed(random_seed)
torch.manual_seed(random_seed)
scaler = MinMaxScaler(feature_range=(1,14))
Aggl_clustering = AgglomerativeClustering(n_clusters=3)

if torch.cuda.is_available():
	torch.cuda.manual_seed_all(random_seed)

def get_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentence_embedding = model.encode(augmented_sentences)
    return sentence_embedding

sentence_embedding = get_embeddings()

umap_3d = UMAP(n_components=3,metric="cosine",n_neighbors=sentence_embedding.shape[0]-1)
umap_embeddings_3d = umap_3d.fit_transform(sentence_embedding)
cluster_labels_3d = Aggl_clustering.fit_predict(umap_embeddings_3d) + 1

umap_coorindates = UMAP(n_components=20,metric="euclidean",n_neighbors=sentence_embedding.shape[0]-1)
embeddings_coordinates = scaler.fit_transform(umap_coorindates.fit_transform(sentence_embedding))
coordinates_labels = Aggl_clustering.fit_predict(embeddings_coordinates)
l1_norms = np.linalg.norm(embeddings_coordinates, ord=1, axis=0)
normalized_coordinates = embeddings_coordinates / l1_norms
print(normalized_coordinates.shape)
umap_2d = UMAP(n_components=2,metric="euclidean",n_neighbors=sentence_embedding.shape[0]-1)
umap_embeddings_2d = umap_2d.fit_transform(sentence_embedding)
cluster_labels_2d = Aggl_clustering.fit_predict(umap_embeddings_3d) + 1
