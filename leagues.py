import pandas as pd

archivo_entrada = "datasets/general/clean_dataset.csv"
df = pd.read_csv(archivo_entrada)
top_5 = set(['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1'])
next_14 = set(['Serie B', 'Belgian Pro League', 'Segunda División', 'Liga Argentina', 'Championship', 'Liga MX', 'Ligue 2',
                'Primeira Liga', 'Saudi Pro League', 'Brasileirao', 'Super Lig', '2.Bundesliga', 'Eredivisie', 'MLS'])

important_columns = ['Gls','Ast','G+A','G-PK','Per 90 Minutes_Gls','Per 90 Minutes_Ast','Per 90 Minutes_G+A',
                     'Per 90 Minutes_G-PK','Per 90 Minutes_G+A-PK','Sh','SoT','SoT%','Sh/90','SoT/90','G/Sh',
                     'G/SoT','Cmp','Att','Cmp%','Short_Cmp','Short_Att','Short_Cmp%','Medium_Cmp','Medium_Att',
                     'Medium_Cmp%','Long_Cmp','Long_Att','Long_Cmp%','A-xAG','KP','1/3','PPA','CrsPA', 'TklW', 
                     'Touches_Touches', 'Touches_Def Pen', 'Touches_Def 3rd', 'Touches_Mid 3rd', 'Touches_Att 3rd', 
                     'Touches_Att Pen', 'Touches_Live', 'Take-Ons_Att', 'Take-Ons_Succ', 'Take-Ons_Succ%', 'Take-Ons_Tkld%', 
                     'Carries_Carries', 'Carries_1/3', 'Carries_CPA', 'Carries_Mis', 'Carries_Dis']

multiplier = pd.Series(1.0, index = df.index)

col_league = 'League'

if col_league in df.columns:
    multiplier[df[col_league].isin(top_5)] = 2.0
    multiplier[df[col_league].isin(next_14)] = 1.5

for col in important_columns:
    df[col] = df[col] * multiplier

df.to_csv("clean_dataset.csv", index=False)