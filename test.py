import pandas as pd


df = pd.read_excel('Aba Produtos - lotes em trânsito (planilha da rede)(1).xlsx')
print(df.head())

cols = [
'Código',
'Batch',
'Amount',
'Validade',
'Chegada Merck',
'Recebimento \nBTG',
'Previsão Liberação Lote',
]

df = df[cols]
print(df.head())
for i in range(len(df)):
    print(type(df.loc[i, 'Validade']))
