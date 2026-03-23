import pandas as pd
import numpy as np

POSITION = {
    'Goalkeeper': 'datasets/players/goalkeepers.csv',
    'Centerback': 'datasets/players/centerbacks.csv',
    'Fullback': 'datasets/players/fullbacks.csv',
    'DMidfielder': 'datasets/players/dmidfielders.csv',
    'CMidfielder': 'datasets/players/cmidfielders.csv',
    'AMidfielder': 'datasets/players/amidfielders.csv',
    'Winger': 'datasets/players/wingers.csv',
    'Forward': 'datasets/players/forwards.csv'
}

def data_loader(search_position):
    file_csv = POSITION.get(search_position)
    if not file_csv:
        raise ValueError(f"Position '{search_position}' not recognized.")
    
    df = pd.read_csv(file_csv)
    return df

def vectorize_data(df, search_team):
    players_teams = df[df['Team'].astype(str).str.contains(search_team, case=False, na=False)]

    if players_teams.empty:
        return None, pd.DataFrame(), pd.DataFrame(), [] 

    numerics_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    ignore_cols = ['Age', 'Real_Salary', 'Market_Value']
    engine_cols = [col for col in numerics_cols if col not in ignore_cols]
    
    average_player_team = players_teams[engine_cols].fillna(0).mean().to_frame().T

    candidates = df[~df['Team'].astype(str).str.contains(search_team, case=False, na=False)].copy()
    max_team_val = players_teams['Market_Value'].max()
    max_team_wage = players_teams['Real_Salary'].max()
    min_team_val = players_teams['Market_Value'][players_teams['Market_Value'] > 0].min() if not players_teams['Market_Value'][players_teams['Market_Value'] > 0].empty else 0
    min_team_wage = players_teams['Real_Salary'][players_teams['Real_Salary'] > 0].min() if not players_teams['Real_Salary'][players_teams['Real_Salary'] > 0].empty else 0
    
    if max_team_val > 0:
        candidates = candidates[candidates['Market_Value'] <= (max_team_val * 1.3)]
    if max_team_wage > 0:
        candidates = candidates[candidates['Real_Salary'] <= (max_team_wage * 1.3)]
    if min_team_val > 0:
        candidates = candidates[candidates['Market_Value'] >= (min_team_val * 0.7)]
    if min_team_wage > 0:
        candidates = candidates[candidates['Real_Salary'] >= (min_team_wage * 0.7)]

    if 'summary_minutesPlayed' in candidates.columns:
         candidates = candidates[candidates['summary_minutesPlayed'] >= 100]
    candidates_num = candidates[engine_cols].fillna(0)

    if candidates.empty:
        return None, players_teams['Player'].tolist()
    
    return average_player_team, candidates, candidates_num, engine_cols
