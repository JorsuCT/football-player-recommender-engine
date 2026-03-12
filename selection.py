import pandas as pd
from data import data_loader, vectorize_data, POSITION
from recommender import get_recomendations

df = "datasets/general/clean_dataset.csv"

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
    average_player_team, candidates, candidates_num, players_base = vectorize_data(df_position, chosen_team)

    if average_player_team is None:
        print(f"No players found for team '{chosen_team}' in position '{chosen_position}'.")
        return
    
    similarities = get_recomendations(average_player_team, candidates_num)

    candidates['Similarity'] = similarities
    recomendations = candidates.sort_values(by='Similarity', ascending=False).head(10)

    print(f"\nRESULT FOR TEAM: {chosen_team} - POSITION: {chosen_position}\n")
    columnas_mostrar = ['Player', 'Age', 'Team', 'League', 'Wage', 'Value', 'Similarity']
    columnas_mostrar = [c for c in columnas_mostrar if c in recomendations.columns]
    print(recomendations[columnas_mostrar].to_string(index=False))
    print("\n")
