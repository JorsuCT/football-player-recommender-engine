import pandas as pd
import numpy as np

POSITION = {
    'Goalkeeper': 'datasets/players/porteros.csv',
    'Centerback': 'datasets/players/centrales.csv',
    'Fullback': 'datasets/players/laterales.csv',
    'Midfielder': 'datasets/players/centrocampistas.csv',
    'Winger': 'datasets/players/extremos.csv',
    'Forward': 'datasets/players/delanteros.csv'
}

def clean_data(valor):
    if pd.isna(valor) or valor == "Sin Dato" or valor == 0:
        return 0.0
    return float(str(valor).replace('.', ''))

def data_loader(search_position):
    archivo_csv = POSITION.get(search_position)
    if not archivo_csv:
        raise ValueError(f"Position '{search_position}' not recognized.")
    
    df = pd.read_csv(archivo_csv)

    if 'Wage' in df.columns:
        df['Wage_Num'] = df['Wage'].apply(clean_data)
    if 'Value' in df.columns:
        df['Value_Num'] = df['Value'].apply(clean_data)
    
    return df

def vectorize_data(df, search_team):
    players_teams = df[df['Team'].astype(str).str.contains(search_team, case=False, na=False)]

    if players_teams.empty:
        return None, [] 

    numerics_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    df_numerico = df[numerics_cols].fillna(0)
    
    average_player_team = players_teams[numerics_cols].fillna(0).mean().values.reshape(1, -1)

    mask_candidates = ~df['Team'].astype(str).str.contains(search_team, case=False, na=False)
    candidates = df[mask_candidates].copy()
    candidates_num = df_numerico[mask_candidates]

    if candidates.empty:
        return None, players_teams['Player'].tolist()
    
    return average_player_team, candidates, candidates_num, players_teams['Player'].tolist()