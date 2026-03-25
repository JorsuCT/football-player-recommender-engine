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

def vectorize_data(df, search_team, target_mode, target_value):
    numerics_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    ignore_cols = ['Age', 'Real_Salary', 'Market_Value', 'Tactical_Role']
    engine_cols = [col for col in numerics_cols if col not in ignore_cols]

    full_population = df[engine_cols].fillna(0)

    if target_mode == "Player":
        target_data = df[df['Player'] == target_value]
        if target_data.empty: return None, pd.DataFrame, pd.DataFrame, pd.DataFrame
        target_role = target_data['Tactical_Role'].values[0] if 'Tactical_Role' in target_data.columns else None
        base_player_vector = target_data[engine_cols].fillna(0)
    elif target_mode == "Role":
        target_role = int(target_value)
        role_players = df[df['Tactical_Role'] == target_role]
        if role_players.empty: return None, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        base_player_vector = role_players[engine_cols].fillna(0).mean().to_frame().T

    candidates = df[~df['Team'].astype(str).str.contains(search_team, case=False, na=False)].copy()

    if target_role is not None:
        candidates = candidates[candidates['Tactical_Role'] == target_role]
    
    players_teams = df[df['Team'].astype(str).str.contains(search_team, case=False, na=False)]
    if not players_teams.empty:
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
    
    return base_player_vector, candidates, candidates_num, full_population
