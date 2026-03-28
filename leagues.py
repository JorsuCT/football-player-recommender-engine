import pandas as pd

file_input = "datasets/general/clean_dataset.csv"
df = pd.read_csv(file_input)

top_5 = set(['Premier League', 'LaLiga', 'Serie A', 'Bundesliga', 'Ligue 1'])

next_14 = set(['Serie B', 'Pro League', 'LaLiga 2', 'Liga Profesional de Fútbol Argentino', 'Championship', 'Liga MX, Clausura', 
'Ligue 2', 'Liga Portugal Betclic', 'Saudi Pro League', 'Brasileirão Betano', 'Trendyol Süper Lig', '2.Bundesliga', 
'VriendenLoterij Eredivisie', 'MLS'])

good_level = set(['Austrian Bundesliga', 'Stoiximan Super League', 'Scottish Premiership', 'Swiss Super League'])

low_level = set(['League One', 'Primera Federación', 'Serie C', '3. Liga', 'Nacional', 'Brasileirão Série B', 'Liga de Primera', 
'A-League', 'Chinese Super League', 'Romanian SuperLiga', 'Premium Liiga', 'Niké Liga', 'National 1', 'Parva Liga', 'Algerian Ligue 1', 
'Fizz Liga', 'Primera A, Apertura', 'Virsliga', 'UAE Pro League', 'A-League Men', 'TOPLYGA', 'Cyprus League by Stoiximan', 
'Erovnuli Liga', 'J1 League', 'K League 1', 'Botola Pro', 'Abissnet Superiore', 'Misli Premier League', 'Israeli Premier League', 
'PrvaLiga', 'Ukrainian Premier League'])

low_low_level = set(['Moldovan Super Liga', 'Tunisian Ligue Professionnelle 1', 'Faroe Islands Premier League', 
                     'Liga Panameña de Fútbol, Clausura', 'Uzbekistan Super League', 'Liga Portugal 2', 'División Profesional',
                     'Cambodian Premier League', 'Indonesia Super League', 'Kazakhstan Premier League', ' Premier Division', 
                     'Indian Super League', 'Tanzanian Premier League', 'NIFL Premiership', 'Singapore Premier League', 
                     'Hong Kong Premier League', 'Iraq Stars League', 'Cymru Premier', 'Kyrgyzstan Top Liga', 
                     'LPR Pro, Apertura', 'Liga 1', 'Stars League', 'South African Premier Division', 'AlbiMall Superliga', 
                     'League Two', 'Malaysia Super League', 'Primera División, Apertura', 'YoHealth Malta Premier', 'Thai League 1', 
                     'WWIN Liga BiH', 'Vysshaya Liga', 'Armenian Premier League', 'Ghana Premier League', 'Persian Gulf Pro League', 
                     'Bangladesh Football Premier League', 'Nigeria Premier Football League', 'V-League 1', 'Primera Divisió', 
                     'Liga Nacional de Fútbol de Guatemala, Clausura', 'Montenegrin First League', 'Chinese Super League', 'Liga FUTVE'])

important_columns = ['Goals','Expected Goals','Successful Dribbles','Tackles','Assists','Big Chances Missed','Total Shots', 
                     'Interceptions','Clearances','Error Lead To Goal','Outfielder Blocks','Big Chances Created','Accurate Passes',
                     'Key Passes','Saves','Clean Sheet']

multiplier = pd.Series(1.0, index = df.index)

col_league = 'League'

if col_league in df.columns:
    multiplier[df[col_league].isin(top_5)] = 2.0
    multiplier[df[col_league].isin(next_14)] = 1.5
    multiplier[df[col_league].isin(good_level)] = 1.2
    multiplier[df[col_league].isin(low_level)] = 0.8
    multiplier[df[col_league].isin(low_low_level)] = 0.5

for col in important_columns:
    df[col] = df[col] * multiplier

df.to_csv("datasets/general/weighted_dataset.csv", index=False)
