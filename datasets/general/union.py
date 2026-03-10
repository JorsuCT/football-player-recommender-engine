import pandas as pd
import numpy as np
import unicodedata
from difflib import SequenceMatcher

def normalizar(texto):
    if pd.isna(texto): return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()

def similitud(a, b):
    return SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()

def limpiar_edad(edad_str):
    try: return int(str(edad_str).split('-')[0])
    except: return -1

def mapear_posicion(pos_stats):
    """Convierte las posiciones de Stats a las de SoFIFA para la Fase 2"""
    p = str(pos_stats).upper()
    posibles = []
    if 'GK' in p: posibles.append('GK')
    if 'DF' in p: posibles.extend(['CB', 'LB', 'RB', 'LWB', 'RWB'])
    if 'MF' in p: posibles.extend(['CDM', 'CM', 'CAM', 'LM', 'RM'])
    if 'FW' in p: posibles.extend(['ST', 'CF', 'LW', 'RW'])
    return posibles

try:
    df_stats = pd.read_csv("stats.csv")
    df_sofifa = pd.read_csv("salaries.csv")
except Exception as e:
    exit()

df_stats['Age_Clean'] = df_stats['5_Age'].apply(limpiar_edad) if '5_Age' in df_stats.columns else df_stats['Age'].apply(limpiar_edad)
col_nombre_stats = '1_Player' if '1_Player' in df_stats.columns else 'Player'
col_equipo_stats = '4_Squad' if '4_Squad' in df_stats.columns else 'Squad'
col_pos_stats = '3_Pos' if '3_Pos' in df_stats.columns else 'Pos'
col_edad_stats = '5_Age' if '5_Age' in df_stats.columns else 'Age'

df_stats['Nombre_Norm'] = df_stats[col_nombre_stats].apply(normalizar)
df_stats['Equipo_Norm'] = df_stats[col_equipo_stats].apply(normalizar)

df_sofifa['Nombre_Norm'] = df_sofifa['Player'].apply(normalizar)
df_sofifa['Equipo_Norm'] = df_sofifa['Squad'].apply(normalizar)

df_stats['Salario_Real_€'] = 0.0
df_stats['Valor_Mercado'] = 0.0
df_stats['Pie_Bueno'] = 'Desconocido'
df_stats['SoFIFA_Match_Name'] = None
df_stats['SoFIFA_Match_Team'] = None
df_stats['Fase_Match'] = None
df_stats['Pos_SalarySport'] = None

sofifa_usados = set()
matches_fase1 = 0
matches_fase2 = 0

sofifa_data = df_sofifa.to_dict('records')

sofifa_data = df_sofifa.to_dict('records')

sofifa_por_edad = {}
for i, cand in enumerate(sofifa_data):
    try:
        e = int(cand['Age_SalarySport'])
        if e not in sofifa_por_edad:
            sofifa_por_edad[e] = []
        sofifa_por_edad[e].append((i, cand))
    except:
        pass

print("FASE 1 iniciada")

for idx, row_stat in df_stats.iterrows():
    nombre_norm_stat = row_stat['Nombre_Norm']
    equipo_norm_stat = row_stat['Equipo_Norm']
    edad_stat = row_stat['Age_Clean']
    
    mejor_score = 0
    mejor_idx_sofifa = -1
    mejor_cand = None
    
    candidatos_validos = []
    for edad_buscada in [edad_stat, edad_stat - 1, edad_stat + 1]:
        if edad_buscada in sofifa_por_edad:
            candidatos_validos.extend(sofifa_por_edad[edad_buscada])

    for i, cand in candidatos_validos:
        if i in sofifa_usados: continue
        
        cand_nombre_norm = cand['Nombre_Norm']
        cand_equipo_norm = cand['Equipo_Norm']

        score_nombre = similitud(nombre_norm_stat, cand_nombre_norm)
        if score_nombre < 0.4: continue 
        
        score_equipo = similitud(equipo_norm_stat, cand_equipo_norm)
        
        apellido_stat = nombre_norm_stat.split()[-1] if nombre_norm_stat else ""
        if apellido_stat and apellido_stat in cand_nombre_norm:
            score_nombre += 0.2
            
        final_score = (score_nombre * 0.7) + (score_equipo * 0.3)
        
        if final_score > 0.65 and final_score > mejor_score:
            mejor_score = final_score
            mejor_idx_sofifa = i
            mejor_cand = cand
            
    if mejor_idx_sofifa != -1:
        df_stats.at[idx, 'Salario_Real_€'] = mejor_cand['Salario_Real_€']
        df_stats.at[idx, 'Valor_Mercado'] = mejor_cand['Valor_Mercado']
        df_stats.at[idx, 'Pie_Bueno'] = mejor_cand.get('Pie_Bueno', 'Desconocido')
        df_stats.at[idx, 'SoFIFA_Match_Name'] = mejor_cand['Player']
        df_stats.at[idx, 'SoFIFA_Match_Team'] = mejor_cand['Squad']
        df_stats.at[idx, 'Fase_Match'] = '1_Nombre'
        df_stats.at[idx, 'Pos_SalarySport'] = mejor_cand['Pos_SalarySport']
        
        sofifa_usados.add(mejor_idx_sofifa)
        matches_fase1 += 1

print("FASE 2 iniciada")

for idx, row_stat in df_stats[df_stats['Salario_Real_€'] == 0].iterrows():
    edad_stat = row_stat['Age_Clean']
    equipo_stat = normalizar(row_stat[col_equipo_stats])
    pos_stat = row_stat[col_pos_stats]
    
    posibles_pos = mapear_posicion(pos_stat)
    
    for i, cand in enumerate(sofifa_data):
        if i in sofifa_usados: continue
        
        try: edad_sofifa = int(cand['Age_SalarySport'])
        except: continue
        
        if abs(edad_sofifa - edad_stat) > 1: continue
        
        equipo_sofifa = normalizar(cand['Squad'])
        if similitud(equipo_stat, equipo_sofifa) < 0.7 and not (set(equipo_stat.split()) & set(equipo_sofifa.split())):
            continue
            
        pos_sofifa = str(cand['Pos_SalarySport']).upper()
        if any(p in pos_sofifa for p in posibles_pos):
            df_stats.at[idx, 'Salario_Real_€'] = cand['Salario_Real_€']
            df_stats.at[idx, 'Valor_Mercado'] = cand['Valor_Mercado']
            df_stats.at[idx, 'Pie_Bueno'] = cand.get('Pie_Bueno', 'Desconocido')
            df_stats.at[idx, 'SoFIFA_Match_Name'] = cand['Player']
            df_stats.at[idx, 'SoFIFA_Match_Team'] = cand['Squad']
            df_stats.at[idx, 'Fase_Match'] = '2_Equipo_Pos'
            df_stats.at[idx, 'Pos_SalarySport'] = cand['Pos_SalarySport']
            
            sofifa_usados.add(i)
            matches_fase2 += 1
            break

def formato_euro(val):
    if pd.isna(val) or val == 0: return "Sin Dato"
    return "{:,.0f}".format(val).replace(",", ".")

df_stats['Salario_Formateado'] = df_stats['Salario_Real_€'].apply(formato_euro)
df_stats['Valor_Formateado'] = df_stats['Valor_Mercado'].apply(formato_euro)

cols_pri = [col_nombre_stats, col_edad_stats, '2_Nation', col_equipo_stats, 
            'Salario_Formateado', 'Valor_Formateado', 'Pie_Bueno', 
            'SoFIFA_Match_Name', 'SoFIFA_Match_Team', 'Fase_Match', 'Pos_SalarySport']
cols_rest = [c for c in df_stats.columns if c not in cols_pri and c != 'Age_Clean']

df_final = df_stats[cols_pri + cols_rest]
df_final.to_csv("dataset_final.csv", index=False)
