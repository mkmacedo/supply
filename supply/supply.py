import pandas as pd


df_vendas = pd.read_excel("Aba Vendas (TRANSAÇÃO SAP)(1).xlsx")
df_produtos = pd.read_excel("Aba Produtos - lotes em trânsito (planilha da rede)(1).xlsx")
df_estoque = pd.read_excel("Lotes estoque (TRANSAÇÃO SAP - bloqueados)(1).xlsx")
df_estoque2 = pd.read_excel("Lotes estoque (TRANSAÇÃO SAP - todos os lotes)(1).xlsx")
df_forecast = pd.read_excel("Aba Forecast (SAP IBP)(1).xlsx")
df_colocado = pd.read_excel("Aba Colocado (planilha da rede-area de trabalho)(1).xlsx")
df_biotech = pd.read_excel("Planejamento Biotech + Stilamin(1).xlsx")




#print(df_biotech.head())
