import streamlit as st
import pandas as pd
from data import data_loader, vectorize_data
from recommender import get_recomendations
import radar

st.set_page_config(page_title="Statistical Football Scout", page_icon="⚽", layout="wide")

@st.cache_data
def load_data():
    df_clean = pd.read_csv("datasets/general/clean_dataset.csv", low_memory=False)
    df_weighted = pd.read_csv("datasets/general/weighted_dataset.csv", low_memory=False)
    return df_clean, df_weighted

df_clean, df_weighted = load_data()

st.sidebar.title("Scouting Filters")
st.sidebar.markdown("---")

available_leagues = sorted(df_weighted['League'].dropna().unique())
chosen_league = st.sidebar.selectbox("Choose your League:", available_leagues)

available_teams = sorted(df_weighted[df_weighted['League'] == chosen_league]['Team'].dropna().unique())
chosen_team = st.sidebar.selectbox("Choose your Team:", available_teams)

available_positions = ['Goalkeeper', 'Centerback', 'Fullback', 'DMidfielder', 
                       'CMidfielder', 'AMidfielder', 'Winger', 'Forward']
chosen_position = st.sidebar.selectbox("Position to develop:", available_positions)

st.sidebar.markdown("---")
st.sidebar.subheader("Financial Adjust")
use_salary_limit = st.sidebar.checkbox("Apply estrict salary limit", value=True)
transfer_margin = st.sidebar.slider("Margin over maket value (%)", min_value=100, max_value=200, value=150, step=10)

st.title("Inteligent Scouting Sistem")
st.markdown(f"**Searching candidates for:** {chosen_team} | **Position:** {chosen_position}")
st.markdown("---")

df_position = data_loader(chosen_position)

strategy = st.radio(
    "Select the searching strategy:",
    ("Exact substitute for a player", "Ideal tactic role")
)

if strategy == "Exact substitute for a player":
    target_mode = 'Player'
    team = sorted(df_position[df_position['Team'] == chosen_team]['Player'].unique())
    if team:
        target_value = st.selectbox("Choose the player to substitute:", team)
    else:
        st.warning("No data for this team.")
        target_value = None
else:
    target_mode = 'Role'
    available_roles = sorted(df_position['Tactical_Role'].dropna().unique())

    st.markdown("### Guide of Tactic Roles:")
    for role in available_roles:
        players_role = df_position[df_position['Tactical_Role'] == role]
        top_players = players_role.sort_values(by='Market_Value', ascending=False).head(3)['Player'].tolist()
        examples = ', '.join(top_players)
        st.caption(f"**Role {int(role)}**: Players like [{examples}]")
    
    target_value = st.selectbox("Select the desired role:", available_roles)


if st.button("Search substitutes", type="primary"):
    with st.spinner('Analizing database'):
        df_position = data_loader(chosen_position)

        base_vector, candidates, candidates_num, full_population = vectorize_data(
            df_position, chosen_team, target_mode, target_value
        )

        if base_vector is None:
            st.error("Error: No enough data for the player.")
        else:
            similarities_weighted, raw_similarities = get_recomendations(
                base_vector, candidates_num, full_population
            )

            candidates = candidates.copy()
            candidates['Similarity'] = similarities_weighted
            candidates['Raw_Similarity'] = raw_similarities

            max_team_val = df_weighted[df_weighted['Team'] == chosen_team]['Market_Value'].mean()
            max_budget = max_team_val * (transfer_margin / 100)

            if target_mode == 'Player':
                candidates = candidates[candidates['Player'] != target_value]
            
            final_candidates = candidates[candidates['Market_Value'] <= max_budget].sort_values(by='Similarity', ascending=False).head(10)

            st.session_state['candidates'] = final_candidates
            st.session_state['target_mode'] = target_mode
            st.session_state['target_value'] = target_value
            st.session_state['df_position'] = df_position

    st.success("Analisys completed.")

if 'candidates' in st.session_state:
    st.markdown("---")
    st.subheader("Top 10 Recommendations:")

    show_candidates = st.session_state['candidates']
    table_cols = ['Player', 'Age', 'Team', 'League', 'Market_Value', 'Similarity']
    st.dataframe(show_candidates[table_cols].reset_index(drop=True), use_container_width=True)

    st.markdown("---")
    st.subheader("Visual Analisys (Interactive Radar):")

    chosen_candidate = st.selectbox(
        "Select a candidate to compare with the target:",
        show_candidates['Player'].to_list()
    )

    if chosen_candidate:
        t_mode = st.session_state['target_mode']
        t_value = st.session_state['target_value']
        df_pos = st.session_state['df_position']

        if 'Goalkeeper' in chosen_position:
            radar_cols = ['Saves', 'Saved Shots From Inside The Box', 'Clean Sheet', 'Penalty Save', 'Runs Out', 
                          'Accurate Passes', 'Accurate Passes Percentage', 'Clearances', 'Error Lead To Goal']
        else:
            radar_cols = ['Goals', 'Expected Goals', 'Goal Conversion Percentage', 'Assists', 'Key Passes', 'Accurate Passes',
                          'Big Chances Created','Successful Dribbles', 'Accurate Passes Percentage', 'Tackles', 'Interceptions', 
                          'Clearances', 'Outfielder Blocks', 'Big Chances Missed', 'Total Shots', 'Error Lead To Goal']
            
        radar_cols = [col for col in radar_cols if col in df_clean.columns]

        pop_raw = df_clean[df_clean['Player'].isin(df_pos['Player'])][radar_cols].fillna(0)
        candidate_raw = df_clean[df_clean['Player'] == chosen_candidate][radar_cols].fillna(0).head(1)

        if target_mode == "Player":
            target_raw = df_clean[df_clean['Player'] == target_value][radar_cols].fillna(0).head(1)
            target_display_name = target_value
        else:
            players_role = df_position[df_position['Tactical_Role'] == target_value]['Player'].unique()
            target_raw = df_clean[df_clean['Player'].isin(players_role)][radar_cols].fillna(0).mean().to_frame().T
            target_display_name = f"Ideal Arqutipe (Role {target_value})"
    
        fig = radar.generate_radar(
            target_name=target_display_name,
            candidate_name=chosen_candidate,
            target_raw=target_raw,
            candidate_raw=candidate_raw,
            population_raw=pop_raw,
            columns=radar_cols
        )

        st.plotly_chart(fig, use_container_width=True)
