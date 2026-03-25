import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

POSITION_FILES = [
    'datasets/players/goalkeepers.csv',
    'datasets/players/centerbacks.csv',
    'datasets/players/fullbacks.csv',
    'datasets/players/dmidfielders.csv',
    'datasets/players/cmidfielders.csv',
    'datasets/players/amidfielders.csv',
    'datasets/players/wingers.csv',
    'datasets/players/forwards.csv'
]

N_CLUSTERS = 4 

print("Starting positional Clustering engine (K-Means)")

for file_path in POSITION_FILES:
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        continue

    numerics_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    ignore_cols = ['Age', 'Real_Salary', 'Market_Value']
    engine_cols = [col for col in numerics_cols if col not in ignore_cols]
    
    df_numerics = df[engine_cols].fillna(0)
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_numerics)
    
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=11037, n_init=10)
    df['Tactical_Role'] = kmeans.fit_predict(scaled_data)
    
    df.to_csv(file_path, index=False)
    
    name_position = file_path.split('/')[-1].replace('.csv', '').upper()
    print(f"Completed {name_position}: Players divided in {N_CLUSTERS} tactic roles.")
