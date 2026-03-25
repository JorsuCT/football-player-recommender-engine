import pandas as pd
from data import data_loader, vectorize_data, POSITION
from recommender import get_recomendations

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
