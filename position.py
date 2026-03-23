import pandas as pd

file_input = "datasets/general/weighted_dataset.csv"
df = pd.read_csv(file_input)

goalkeepers = []
centerbacks = []
fullbacks = []
dmidfielders = []
cmidfielders = []
wingers = []
forwards = []

for idx, row_stat in df.iterrows():
    if 'GK' in str(df.loc[idx, 'Positions']):
        goalkeepers.append(df.loc[idx])
    if 'CB' in str(df.loc[idx, 'Positions']):
        centerbacks.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Positions']) for p in ['LB', 'RB', 'RWB', 'LWB']):
        fullbacks.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Positions']) for p in ['DM', 'CM']):
        dmidfielders.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Positions']) for p in ['CM', 'AM']):
        cmidfielders.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Positions']) for p in ['RW', 'LW', 'RM', 'LM']):
        wingers.append(df.loc[idx])
    if any(p in str(df.loc[idx, 'Positions']) for p in ['ST']):
        forwards.append(df.loc[idx])

goalkeepers_df = pd.DataFrame(goalkeepers)
centerbacks_df = pd.DataFrame(centerbacks)
fullbacks_df = pd.DataFrame(fullbacks)
cmidfielders_df = pd.DataFrame(cmidfielders)
dmidfielders_df = pd.DataFrame(dmidfielders)
wingers_df = pd.DataFrame(wingers)
forwards_df = pd.DataFrame(forwards)

goalkeepers_df.to_csv("datasets/players/goalkeepers.csv", index=False)
centerbacks_df.to_csv("datasets/players/centerbacks.csv", index=False)
fullbacks_df.to_csv("datasets/players/fullbacks.csv", index=False)
dmidfielders_df.to_csv("datasets/players/dmidfielders.csv", index=False)
cmidfielders_df.to_csv("datasets/players/cmidfielders.csv", index=False)
wingers_df.to_csv("datasets/players/wingers.csv", index=False)
forwards_df.to_csv("datasets/players/forwards.csv", index=False)
