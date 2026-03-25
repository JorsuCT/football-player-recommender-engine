import pandas as pd
from data import data_loader, vectorize_data, POSITION
from recommender import get_recomendations
import radar
import numpy as np

df = "datasets/general/weighted_dataset.csv"

def select_option(list_options, title):
    print(f"\n--- {title.upper()} ---")
    for i, option in enumerate(list_options, 1):
        print(f"{i}. {option}")
        
    while True:
        try:
            seleccion = int(input(f"\nIntroduce a number (1-{len(list_options)}): "))
            if 1 <= seleccion <= len(list_options):
                return list_options[seleccion - 1]
            else:
                print("Non valid option. Please choose a number from the list.")
        except ValueError:
            print("Invalid input. You must enter a number.")

def start_engine():
    try:
        df_general = pd.read_csv(df)
    except FileNotFoundError:
        print(f"Could not find {df}.")
        return
        
    leagues = sorted(df_general['League'].dropna().unique())
    chosen_league = select_option(leagues, "Leagues")
    
    teams = sorted(df_general[df_general['League'] == chosen_league]['Team'].dropna().unique())
    chosen_team = select_option(teams, f"Equipos de {chosen_league}")
    
    positions = list(POSITION.keys())
    chosen_position = select_option(positions, "Posiciones")
    df_position = data_loader(chosen_position)

    while True:
        strategy = input("Chose strategy (1 -Player from team- or 2 -Role of players-): ")
        if strategy in ['1', '2']: break
    
    if strategy == '1':
        target_mode = "Player"
        team_players = df_position[df_position['Team'].astype(str).str.contains(chosen_team, case=False, na=False)]
        if team_players.empty:
            print(f"No players registered as {chosen_position} in {chosen_team}")
        players_list = sorted(team_players['Player'].unique())
        target_value = select_option(players_list, f"Player to substitute {chosen_position}.")

    else: 
        target_mode = "Role"
        available_roles = sorted(df_position['Tactical_Role'].dropna().unique())
        for role in available_roles:
            players_role = df_position[df_position['Tactical_Role'] == role]
            top_players = players_role.sort_values(by='Market_Value', ascending=False).head(3)['Player'].tolist()
            examples = ", ".join(top_players)
            print(f"Role {int(role)}: Players like [{examples}]")

        while True:
            try:
                role_searched = int(input("\nIntroduce the number of role you want to search: "))
                if role_searched in available_roles:
                    target_value = role_searched
                    break
                else:
                    print("Introduce a valid number.")
            except ValueError:
                print("Introduce a number.")
    
    base_vector, candidates, candidates_num, full_population = vectorize_data(df_position, chosen_team, target_mode, target_value)

    if base_vector is None:
        print(f"No players found for team '{chosen_team}'.")
        return
    
    similarities, raw_similarities = get_recomendations(base_vector, candidates_num, full_population)

    candidates['Similarity'] = similarities
    candidates['Raw_Similarity'] = raw_similarities
    recomendations = candidates.sort_values(by='Similarity', ascending=False).head(10)

    print(f"\nRESULT FOR {chosen_team} \nTARGET: {target_value} - {chosen_position}\n")
    columns_show = ['Player', 'Age', 'Team', 'League', 'Real_Salary', 'Market_Value', 'Similarity', 'Raw_Similarity', 'Tactical_Role']
    columns_show = [c for c in columns_show if c in recomendations.columns]
    print(recomendations[columns_show].to_string(index=False))
    print("\n")

    candidates_name = recomendations['Player'].tolist()
    print("\nSelect candidate to compare:")
    
    for i, name in enumerate(candidates_name, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            selection = int(input(f"\nIntroduce the number (1-{len(candidates_name)}):"))
            if 1 <= selection <= len(candidates_name):
                candidate_chosen = candidates_name[selection - 1]
                break
            else:
                print("Invalid option.")
        except ValueError:
            print("Introduce a valid number.")
    
    try: 
        df_clean = pd.read_csv("datasets/general/clean_dataset.csv", low_memory=False)
    except FileNotFoundError:
        return

    if chosen_position == 'Goalkeeper':
        radar_cols = ['Saves', 'Saved Shots From Inside The Box', 'Clean Sheet', 'Penalty Save', 'Runs Out', 
                      'Accurate Passes', 'Accurate Passes Percentage', 'Clearances', 'Error Lead To Goal']
    else:
        radar_cols = ['Goals', 'Expected Goals', 'Goal Conversion Percentage', 'Assists', 'Key Passes', 'Accurate Passes',
                      'Big Chances Created','Successful Dribbles', 'Accurate Passes Percentage', 'Tackles', 'Interceptions', 
                      'Clearances', 'Outfielder Blocks', 'Big Chances Missed', 'Total Shots', 'Error Lead To Goal']
    
    radar_cols = [col for col in radar_cols if col in df_clean.columns]

    names_position = df_position['Player'].unique()
    pop_raw = df_clean[df_clean['Player'].isin(names_position)][radar_cols].fillna(0)

    candidate_raw = df_clean[df_clean['Player'] == candidate_chosen][radar_cols].fillna(0).head(1)

    if target_mode == "Player":
        target_raw = df_clean[df_clean['Player'] == target_value][radar_cols].fillna(0).head(1)
        target_display_name = target_value
    else:
        players_role = df_position[df_position['Tactical_Role'] == target_value]['Player'].unique()
        target_raw = df_clean[df_clean['Player'].isin(players_role)][radar_cols].fillna(0).mean().to_frame().T
        target_display_name = f"Ideal Arqutipe (Role {target_value})"
    
    radar.generate_radar(
        target_name=target_display_name,
        candidate_name=candidate_chosen,
        target_raw=target_raw,
        candidate_raw=candidate_raw,
        population_raw=pop_raw,
        columns=radar_cols
    )
