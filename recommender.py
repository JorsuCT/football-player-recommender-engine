from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


def get_recomendations(base_average_player, candidates_matrix):
    """
    Motor principal. Recibe parámetros estáticos y devuelve un DataFrame con los resultados.
    """
    scaler = StandardScaler()

    scaler.fit(candidates_matrix)

    candidates_scaled = scaler.transform(candidates_matrix)
    scaled_base_player = scaler.transform(base_average_player)

    similarities = cosine_similarity(scaled_base_player, candidates_scaled)[0]

    return similarities.round(2)
