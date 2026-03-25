from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import numpy as np


def get_recomendations(base_average_player, candidates_matrix, full_population_matrix):
    """ Main engine. Recibes the static parameters and returns a DataFrame with the results. """
    scaler = StandardScaler()

    scaler.fit(full_population_matrix)
    
    candidates_matrix['Error Lead To Goal'] = candidates_matrix['Error Lead To Goal'] * -1
    candidates_matrix['Big Chances Missed'] = candidates_matrix['Big Chances Missed'] * -1
    
    candidates_scaled = scaler.transform(candidates_matrix)
    scaled_base_player = scaler.transform(base_average_player)

    similarities = cosine_similarity(scaled_base_player, candidates_scaled)[0]

    quality_index = np.sum(candidates_scaled, axis=1)

    min_quality = np.min(quality_index)
    max_quality = np.max(quality_index)
    if max_quality > min_quality:
        quality_index_normalized = (quality_index - min_quality) / (max_quality - min_quality)
    else:
        quality_index_normalized = np.zeros_like(quality_index)
    
    similarities_weighted = similarities * 0.7 + quality_index_normalized * 0.3

    return similarities_weighted.round(2), similarities.round(2)
