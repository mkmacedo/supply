import pandas as pd
import sys

#filename = sys.argv[1]
#csv_df = pd.read_csv(r'Arquivo_JDA.csv', on_bad_lines='skip')

#csv_df.to_excel('saida.xlsx')

df = pd.read_excel('Arquivo-JDA_2_.xlsx')

print(df.head())