import pandas as pd
import numpy as np

network1 = pd.read_csv('cell_lines_BBSR1.1_ChromPrior_TfsPrior.tsv', sep = '\t')
network2 = pd.read_csv('cell_lines_BBSR1.1_TrrustPrior_TfsPrior.tsv', sep = '\t')

# TRRUST prior -- grouped predictors
# pred.group.1 -> 'RFXANK' 'RFXAP'
grouped_predictors = network2.loc[network2['regulator'] == 'pred.group.1',:]
ungrouped = []
for interaction, row in grouped_predictors.iterrows():
    tmp_row = row.copy()
    tmp_row['regulator'] = 'RFXANK'
    ungrouped.append(tmp_row)
    tmp_row = row.copy()
    tmp_row['regulator'] = 'RFXAP'
    ungrouped.append(tmp_row)
ungrouped = pd.DataFrame(ungrouped)
network2 = pd.concat([network2, ungrouped])
network2 = network2.loc[~(network2['regulator'] == 'pred.group.1'),:]

network1['prior'] = 'CHROM'
network2['prior'] = 'TRRUST'

network = pd.concat([network1, network2])
network_final = []

for interaction, df in network.groupby(['regulator', 'target']):
    df = df.loc[:,['regulator', 'target', 'beta.sign.sum', 'prior']]
    if df.shape[0] > 1:
        value = np.sign(df['beta.sign.sum'][df['prior'] == 'TRRUST'])*(np.abs(df['beta.sign.sum'].tolist()).max())
        df['beta.sign.sum'] = value
        df['prior'] = 'BOTH'
        df = df.dropna()
    network_final.append(df)

network_final = pd.concat(network_final)
network_final = network_final.iloc[:,[0,1,2]]
network_final.columns = ['regulator', 'target', 'bootstraps']
network_final.loc[:,'bootstraps'] = network_final['bootstraps'].astype(str)

network_final.to_csv('cell_lines_BBSR1.1_combinedPriors_TfsPriors.tsv', sep = '\t', index = False)
