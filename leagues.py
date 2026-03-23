import pandas as pd

file_input = "datasets/general/clean_dataset.csv"
df = pd.read_csv(file_input)
top_5 = set(['Premier League', 'LaLiga', 'Serie A', 'Bundesliga', 'Ligue 1'])
next_14 = set(['Serie B', 'Pro League', 'Segunda División', 'Primera División (Argentina)', 'Championship', 'Liga MX', 'Ligue 2',
                'Primeira Liga', 'Saudi Pro League', 'Brasileirao', 'Super Lig', '2.Bundesliga', 'Eredivisie', 'MLS'])
low_level = set(['EFL', 'Primera / Segunda RFEF', 'Serie C', '3. Liga', 'Nacional', 'Ascenso (Argentina)', 'Serie B / Ascenso (Brasil)',
                 'Chilean Primera División', 'A-League', 'Chinese Super League', ])

important_columns = ['Goals','Expected Goals','Successful Dribbles','Tackles','Assists','Big Chances Missed','Total Shots', 
                     'Interceptions','Clearances','Error Lead To Goal','Outfielder Blocks','Big Chances Created','Accurate Passes',
                     'Key Passes','Saves','Clean Sheet']

multiplier = pd.Series(1.0, index = df.index)

col_league = 'League'

if col_league in df.columns:
    multiplier[df[col_league].isin(top_5)] = 2.0
    multiplier[df[col_league].isin(next_14)] = 1.5
    multiplier[df[col_league].isin(low_level)] = 0.8

for col in important_columns:
    df[col] = df[col] * multiplier

df.to_csv("weighted_dataset.csv", index=False)