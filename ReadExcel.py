import pandas as pd
import sys

#pln1 = sys.argv[1]
#pln2 = sys.argv[2]
#pln3 = sys.argv[3]
#pln4 = sys.argv[4]
#pln5 = sys.argv[5]
#pln6 = sys.argv[6]
#pln7 = sys.argv[7]

filenames = sys.stdin.read()
print(filenames)

sheets = filenames.split('\n')

#df_vendas = pd.read_excel(pln1)
#df_produtos = pd.read_excel(pln2)
#df_estoque_blocked = pd.read_excel(pln3)
#df_estoque_all = pd.read_excel(pln4)
#df_forecast = pd.read_excel(pln5)
#df_colocado = pd.read_excel(pln6)
#df_biotech = pd.read_excel(pln7)
#

df_vendas = pd.read_excel(sheets[0].strip())
df_produtos = pd.read_excel(sheets[1].strip())
df_estoque_blocked = pd.read_excel(sheets[2].strip())
df_estoque_all = pd.read_excel(sheets[3].strip())
df_forecast = pd.read_excel(sheets[4].strip())
df_colocado = pd.read_excel(sheets[5].strip())
df_biotech = pd.read_excel(sheets[6].strip())

material = df_estoque_all['Material No']
material = material.unique()

d = {}

for f in material:
    temp_df = pd.DataFrame()
    d[f] = {}
    
    for i in range(len(df_estoque_all)):
        if str(df_estoque_all.loc[i, 'Material No']) == f:
            d[f]['Batch'] = str(df_estoque_all.loc[i, 'Batch'])
            d[f]['Stock'] = str(df_estoque_all.loc[i, 'Stock'])
            d[f]['Plant'] = str(df_estoque_all.loc[i, 'Plant'])
            d[f]['Batch status key']  = str(df_estoque_all.loc[i, 'Batch status key'])
            d[f]['Expiration date'] = str(df_estoque_all.loc[i, 'Expiration date'])


    for i in range(len(df_vendas)):
        for key in list(d.keys()):

            if df_vendas.loc[i, 'Material'] == key:

                if df_vendas.loc[i, 'Batch'] == d[key]['Batch']:
                    d[key]['Quantity'] = str(df_vendas.loc[i, 'Quantity'])

print(d)





#    if str(f) == str(df_vendas.loc[i, 'Material']):
#        codigo_material = [(df_vendas.loc[i, 'Material'], df_vendas.loc[i, 'Material description'], df_vendas.loc[i, 'Quantity']) for i in range(len(df_vendas[['Material']]))]
#
#prod = {}
#for t in codigo_material:
#    t


#print(codigo_material)


#print(df_biotech.head())
