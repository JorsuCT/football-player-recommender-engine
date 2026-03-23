import pandas as pd
import numpy as np

POSITION = {
    'Goalkeeper': 'datasets/players/goalkeepers.csv',
    'Centerback': 'datasets/players/centerbacks.csv',
    'Fullback': 'datasets/players/fullbacks.csv',
    'DMidfielder': 'datasets/players/defensivemidfielders.csv',
    'CMidfielder': 'datasets/players/cmidfielders.csv',
    'AMidfielder': 'datasets/players/amidfielders.csv',
    'Winger': 'datasets/players/wingers.csv',
    'Forward': 'datasets/players/forwards.csv'
}

def clean_data(value):
    if pd.isna(value) or value == "No Data" or value == 0:
        return 0.0
    return float(str(value).replace('.', ''))

def data_loader(search_position):
    file_csv = POSITION.get(search_position)
    if not file_csv:
        raise ValueError(f"Position '{search_position}' not recognized.")
    
    df = pd.read_csv(file_csv)

    if 'Real_Salary' in df.columns:
        df['Wage_Num'] = df['Real_Salary'].apply(clean_data)
    if 'Value' in df.columns:
        df['Value_Num'] = df['Market_Value'].apply(clean_data)
    
    return df

def vectorize_data(df, search_team):
    players_teams = df[df['Team'].astype(str).str.contains(search_team, case=False, na=False)]

    if players_teams.empty:
        return None, [] 

    numerics_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    ignore_cols = ['Age']
    engine_cols = [col for col in numerics_cols if col not in ignore_cols]
    
    average_player_team = players_teams[engine_cols].fillna(0).mean().values.reshape(1, -1)

    mask_candidates = ~df['Team'].astype(str).str.contains(search_team, case=False, na=False)
    candidates = df[mask_candidates].copy()
    candidates_num = candidates[engine_cols].fillna(0)

    if candidates.empty:
        return None, players_teams['Player'].tolist()
    
    return average_player_team, candidates, candidates_num, players_teams['Player'].tolist()
