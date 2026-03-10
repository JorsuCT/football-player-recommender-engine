import pandas as pd

archivo_entrada = "clean_dataset.csv"
df = pd.read_csv(archivo_entrada)

porteros = []
centrales = []
laterales = []
centrocampistas = []
extremos = []
delanteros = []

for idx, row_stat in df.iterrows():
    if 'GK' in str(df.loc[idx, 'Pos']):
        porteros.append(df.loc[idx])
    if 'CB' in str(df.loc[idx, 'Pos']):
        centrales.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Pos']) for p in ['LB', 'RB', 'RWB', 'LWB']):
        laterales.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Pos']) for p in ['CDM', 'CM', 'CAM']):
        centrocampistas.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Pos']) for p in ['RW', 'LW', 'RM', 'LM']):
        extremos.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Pos']) for p in ['ST', 'CF']):
        delanteros.append(df.loc[idx])

porteros_df = pd.DataFrame(porteros)
centrales_df = pd.DataFrame(centrales)
laterales_df = pd.DataFrame(laterales)
centrocampistas_df = pd.DataFrame(centrocampistas)
extremos_df = pd.DataFrame(extremos)
delanteros_df = pd.DataFrame(delanteros)

porteros_df.to_csv("porteros.csv", index=False)
centrales_df.to_csv("centrales.csv", index=False)
laterales_df.to_csv("laterales.csv", index=False)
centrocampistas_df.to_csv("centrocampistas.csv", index=False)
extremos_df.to_csv("extremos.csv", index=False)
delanteros_df.to_csv("delanteros.csv", index=False)
