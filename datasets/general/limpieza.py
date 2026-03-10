import re
import pandas as pd
import numpy as np

archivo_entrada = "dataset_final.csv"
df = pd.read_csv(archivo_entrada, encoding = 'utf-8-sig')

col_borrar = ['0_Rk', '6_Born', '3_Pos', '4_Squad', 'SoFIFA_Match_Name', 'Fase_Match', 'Nombre_Norm', 'Equipo_Norm',
              '18_Matches', '20_Matches', '24_Matches', '26_Matches', '28_Matches', 'Matches', 'Playing Time_Mn/MP',
              'Playing Time_Min%', 'Starts_Mn/Start', 'Starts_Compl', 'Salario_Real_€', 'Valor_Mercado']

df.drop(columns = [c for c in col_borrar if c in df.columns], inplace=True)

def limpiar_nombre(col):
    if col == 'Pos_SalarySport': return 'Pos'
    if col == 'Salario_Formateado': return 'Wage'
    if col == 'Valor_Formateado': return 'Value'
    if col == 'SoFIFA_Match_Team': return 'Team'
    if col == 'Pie_Bueno': return 'Preferred_Foot'
    if col == 'Liga': return 'League'

    col_limpia = re.sub(r'^(Standard|Total|Tackles|Challenges|Blocks|Performance|Playing Time|Starts|Subs|Team Success|Penalty Kicks|\d+)_', '', col)
    return col_limpia

df.columns = [limpiar_nombre(c) for c in df.columns]
df = df.loc[:, ~df.columns.duplicated()]

if 'Nation' in df.columns:
    df['Nation'] = df['Nation'].astype(str).apply(lambda x: x.split(' ')[-1] if ' ' in x else x)

if 'Age' in df.columns:
    df['Age'] = df['Age'].astype(str).apply(lambda x: x.split('-')[0])

cols_clave = ['Player', 'Nation']
cols_texto = ['Pos', 'Team', 'League', 'Age', 'Preferred_Foot']

cols_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

reglas = {}

for col in cols_numericas: 
    if '%' in col or '/' in col or '90s' in col:
        reglas[col] = 'mean'
    else:
        reglas[col] = 'sum'

reglas['Age'] = 'max'

for col in cols_texto: 
    if col in df.columns:
        if col == 'Team':
            reglas[col] = lambda x: ' / '.join(sorted(set(str(v) for v in x if pd.notnull(v))))
        else:
            reglas[col] = 'first'

if 'Wage' in df.columns: reglas['Wage'] = 'max'
if 'Value' in df.columns: reglas['Value'] = 'max'

df_final = df.groupby(cols_clave, as_index = False).agg(reglas)

minutos = df_final['Min']
partidos_90 = minutos / 90

def recalcular_ratio(df_temp, col_target, numerador, denominador_series):
    if numerador in df_temp.columns:
        df_temp[col_target] = np.where(denominador_series > 0, df_temp[numerador] / denominador_series, 0)
        df_temp[col_target] = df_temp[col_target].round(2)

recalculos_90 = {
    '90s_Gls': 'Gls',
    '90s_Ast': 'Ast',
    '90s_G+A': 'G+A',
    '90s_G-PK': 'G-PK',
}

for col_final, col_origen in recalculos_90.items():
    recalcular_ratio(df_final, col_final, col_origen, partidos_90)

cols_front = ['Player', 'Age', 'Nation', 'Pos', 'Team', 'League', 'Preferred_Foot', 'Wage', 'Value']
cols_front = [c for c in cols_front if c in df_final.columns]
cols_rest = [c for c in df_final.columns if c not in cols_front]

df_final = df_final[cols_front + cols_rest]

ligas = {
    ('Athletic Club', 'Atlético Madrid','CA Osasuna', 'Deportivo Alavés', 'Elche CF', 'FC Barcelona', 'Getafe CF', 'Girona FC', 'Levante UD', 'RC Celta', 'RCD Espanyol', 'RCD Mallorca', 'Rayo Vallecano', 'Real Betis Balompié', 'Real Madrid', 'Real Oviedo', 'Real Sociedad', 'Sevilla FC', 'Valencia CF', 'Villarreal CF') : 'La Liga',
    ('AFC Bournemouth', 'Arsenal', 'Aston Villa', 'Brentford', 'Brighton & Hove Albion', 'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham FC', 'Leeds United', 'Liverpool', 'Manchester City', 'Manchester United', 'Newcastle United', 'Nottingham Forest', 'Sunderland','Tottenham Hotspur', 'West Ham United', 'Wolverhampton Wanderers') : 'Premier League',
    ('AC Milan', 'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina', 'Genoa', 'Hellas Verona FC', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese') : 'Serie A',
    ('1. FC Heidenheim 1846', '1. FC Köln', '1. FC Union Berlin', '1. FSV Mainz 05', 'Bayer 04 Leverkusen', 'Borussia Dortmund', 'Borussia Mönchengladbach', 'Eintracht Frankfurt', 'FC Augsburg', 'FC Bayern München', 'FC St. Pauli', 'Hamburger SV', 'RB Leipzig', 'SC Freiburg', 'SV Werder Bremen', 'TSG 1899 Hoffenheim', 'VfB Stuttgart', 'VfL Wolfsburg') : 'Bundesliga',
    ('AJ Auxerre', 'AS Monaco', 'Angers SCO', 'FC Lorient', 'FC Metz', 'FC Nantes', 'Le Havre AC', 'Lille OSC', 'OGC Nice', 'Olympique Lyonnais', 'Olympique de Marseille', 'Paris FC', 'Paris Saint-Germain', 'RC Lens', 'RC Strasbourg Alsace', 'Stade Brestois 29', 'Stade Rennais FC', 'Toulouse FC') : 'Ligue 1',
    ('Birmingham City', 'Blackburn Rovers', 'Bristol City', 'Charlton Athletic', 'Coventry City', 'Derby County', 'Hull City', 'Ipswich Town', 'Leicester City', 'Middlesbrough', 'Millwall FC', 'Norwich City', 'Oxford United', 'Portsmouth', 'Preston North End', 'Queens Park Rangers', 'Sheffield United', 'Sheffield Wednesday', 'Southampton', 'Stoke City', 'Swansea City', 'Watford', 'West Bromwich Albion', 'Wrexham') : 'Championship',
    ('AD Ceuta FC', 'Albacete Balompié', 'Burgos CF', 'CD Castellón', 'CD Leganés', 'CD Mirandés', 'Cultural Leonesa', 'Cádiz CF', 'Córdoba CF', 'FC Andorra', 'Granada CF', 'Málaga CF', 'RC Deportivo de La Coruña', 'Racing Santander', 'Real Sociedad de Fútbol B', 'Real Sporting de Gijón', 'Real Valladolid CF', 'Real Zaragoza', 'SD Eibar', 'SD Huesca', 'UD Almería', 'UD Las Palmas'): 'Segunda División',
    ('Avellino', 'Calcio Padova', 'Carrarese', 'Catanzaro', 'Cesena FC', 'Empoli', 'Frosinone', 'Mantova', 'Modena', 'Monza', 'Palermo FC', 'Pescara', 'Reggiana', 'SS Juve Stabia', 'SSC Bari', 'Sampdoria', 'Spezia', 'Südtirol', 'Venezia', 'Virtus Entella'): 'Serie B',
    ('1. FC Kaiserslautern', '1. FC Magdeburg', '1. FC Nürnberg', 'DSC Arminia Bielefeld', 'Dynamo Dresden', 'Eintracht Braunschweig', 'FC Schalke 04', 'Fortuna Düsseldorf', 'Hannover 96', 'Hertha BSC', 'Holstein Kiel', 'Karlsruher SC', 'SC Paderborn 07', 'SC Preußen Münster', 'SV Darmstadt 98', 'SV Elversberg', 'SpVgg Greuther Fürth', 'VfL Bochum 1848'): '2.Bundesliga',
    ('AS Nancy Lorraine', 'AS Saint-Étienne', 'Amiens SC', 'Clermont Foot 63', 'ESTAC Troyes', 'En Avant Guingamp', 'FC Annecy', 'Grenoble Foot 38', 'Le Mans FC', 'Montpellier HSC', 'Pau FC', 'Red Star FC', 'Rodez Aveyron Football', 'Sporting Club Bastia', 'Stade Lavallois Mayenne FC', 'Stade de Reims', 'US Boulogne Cote d\'Opale', 'USL Dunkerque'): 'Ligue 2',
    ('AVS Futebol SAD', 'Alverca', 'CD Nacional', 'CD Tondela', 'Casa Pia', 'Estrela da Amadora', 'FC Arouca', 'FC Lorient', 'FC Porto', 'Famalicão', 'GD Estoril Praia', 'Gil Vicente FC', 'Moreirense FC', 'Rio Ave FC', 'SL Benfica', 'Santa Clara', 'Sporting CP', 'Sporting Clube de Braga', 'Vitória SC'): 'Primeira Liga',
    ('AZ Alkmaar', 'Ajax', 'Excelsior', 'FC Groningen', 'FC Twente', 'FC Utrecht', 'FC Volendam', 'Feyenoord', 'Fortuna Sittard', 'Go Ahead Eagles', 'Heracles Almelo', 'NAC Breda', 'NEC Nijmegen', 'PEC Zwolle', 'PSV', 'SC Heerenveen', 'Sparta Rotterdam', 'Telstar'): 'Eredivisie',
    ('Atlético Mineiro', 'Bahia', 'Botafogo', 'Corinthians', 'Cruzeiro', 'Flamengo', 'Fluminense', 'Grêmio', 'Internacional', 'Palmeiras', 'São Paulo', 'Vasco da Gama', 'Vitória'): 'Brasileirao',
    ('Argentinos Juniors', 'Atlético Tucumán', 'Barracas Central', 'Belgrano de Córdoba', 'Boca Juniors', 'CA Aldosivi', 'CA Banfield', 'Central Cordoba SdE', 'Club Atlético San Martín', 'Club Atlético Sarmiento', 'Club Atlético Unión', 'Defensa y Justicia', 'Deportivo Riestra', 'Estudiantes de La Plata', 'Gimnasia y Esgrima La Plata', 'Huracán', 'Independiente', 'Independiente Rivadavia', 'Instituto Atlético Central Córdoba', 'Lanús', 'Newell\'s Old Boys', 'Platense', 'Racing Club', 'River Plate', 'Rosario Central', 'San Lorenzo de Almagro', 'Talleres', 'Tigre', 'Vélez Sarsfield'): 'Liga Argentina',
    ('Atlanta United', 'Austin FC', 'CF Montréal', 'Charlotte FC', 'Chicago Fire', 'Colorado Rapids', 'Columbus Crew', 'DC United', 'FC Cincinnati', 'FC Dallas', 'Houston Dynamo', 'Inter Miami', 'LA Galaxy', 'Los Angeles FC', 'Minnesota United FC', 'Nashville SC', 'New England Revolution', 'New York City FC', 'New York Red Bulls', 'Orlando City SC', 'Philadelphia Union', 'Portland Timbers', 'Real Salt Lake', 'San Diego FC', 'San Jose Earthquakes', 'Seattle Sounders FC', 'Sporting Kansas City', 'St. Louis CITY SC', 'Toronto FC', 'Vancouver Whitecaps FC'): 'MLS',
    ('Atlético Tucumán'): 'Liga MX',
    ('Cercle Brugge KSV', 'Club Brugge KV', 'FCV Dender EH', 'KAA Gent', 'KRC Genk', 'KV Mechelen', 'KVC Westerlo', 'Oud-Heverlee Leuven', 'RAAL La Louvière', 'RSC Anderlecht', 'Royal Antwerp FC', 'Royal Charleroi Sporting Club', 'SV Zulte Waregem', 'Sint-Truidense VV', 'Standard de Liège', 'Union Saint-Gilloise'): 'Belgian Pro League',
    ('Alanyaspor', 'Antalyaspor', 'Beşiktaş JK', 'Eyüpspor', 'Fatih Karagümrük', 'Fenerbahçe SK', 'Galatasaray SK', 'Gaziantep FK', 'Gençlerbirliği SK', 'Göztepe SK', 'Kasımpaşa SK', 'Kayserispor', 'Kocaelispor', 'Konyaspor', 'Medipol Başakşehir FK', 'Samsunspor', 'Trabzonspor', 'Çaykur Rizespor'): 'Super Lig',
    ('Al Ahli SFC', 'Al Akhdoud Saudi Club', 'Al Ettifaq', 'Al Fateh', 'Al Fayha', 'Al Hazem FC', 'Al Hilal', 'Al Ittihad', 'Al Khaleej', 'Al Kholood', 'Al Nassr', 'Al Qadsiah FC', 'Al Riyadh', 'Al Shabab', 'Al Taawoun FC', 'Al-Najma SC', 'Damac FC', 'NEOM SC'): 'Saudi Pro League'
}

def corregir_liga(fila):
    equipo_actual = str(fila['Team']).lower()
    for grupo_equipos, liga_correcta in ligas.items():
        for equipo_diccionario in grupo_equipos:
            if equipo_diccionario.lower() in equipo_actual:
                return liga_correcta
            
    return fila['League']

if 'Team' in df_final.columns and 'League' in df_final.columns:
    df_final['League'] = df_final.apply(corregir_liga, axis=1)

archivo_salida = "clean_dataset.csv"
df_final.to_csv(archivo_salida, index=False)
