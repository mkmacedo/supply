from cmath import nan
from datetime import date, datetime, timedelta
import math
from operator import index
from matplotlib.pyplot import axes, axis
import pandas as pd
import regexes
import sys
import numpy as np

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

#self.df_vendas = pd.read_excel(pln1)
#df_produtos = pd.read_excel(pln2)
#df_estoque_blocked = pd.read_excel(pln3)
#self.df_estoque_all = pd.read_excel(pln4)
#df_forecast = pd.read_excel(pln5)
#self.df_colocado = pd.read_excel(pln6)
#df_biotech = pd.read_excel(pln7)
#

class Medicamentos:
    
    def __init__(self, sheets):

        self.df_vendas = pd.read_excel(sheets[0].strip())
        self.df_produtos = pd.read_excel(sheets[1].strip())
        self.df_estoque_blocked = pd.read_excel(sheets[2].strip())
        self.df_estoque_all = pd.read_excel(sheets[3].strip())
        self.df_forecast = pd.read_excel(sheets[4].strip())
        self.df_colocado = pd.read_excel(sheets[5].strip())
        self.df_biotech = pd.read_excel(sheets[6].strip())

        self.d = {}

    def calcular(self, month, estoque_inicial=None):

        material = self.df_estoque_all['Material No']
        material = material.unique()

        test = {}
        
        for f in material:

            self.d[f] = {}
            self.d[f]['Sales'] = 0
            self.d[f]['Delivery'] = ''
            self.d[f]['Colocado'] = 0
            self.d[f]['Batch'] = {}

            for i in range(len(self.df_vendas)):
                if str(self.df_vendas.loc[i, 'Material']) == f:
                    self.d[f]['Sales'] += self.df_vendas.loc[i, 'Quantity'] * (-1)

            for i in range(len(self.df_colocado)):
                if str(self.df_colocado.loc[i, 'Código']) == f:# and str(self.df_colocado.loc[i, 'Código']).replace('.','').replace(',','').isdigit():
                    self.d[f]['Colocado'] = self.df_colocado.loc[i, 'Colocado']
            
            for key in list(self.d.keys()):
                try:
                    self.d[key]['Delivery'] = self.d[f]['Colocado'] - self.d[f]['Sales']
                    #print('Try SALES',self.d[f]['Sales'])
                    #print('Try COLOCADO',self.d[f]['Colocado'])
                    #print('Try DELIVERY', self.d[key]['Delivery'])
                except:
                    pass
            
            
            for i in range(len(self.df_estoque_all)):

                if str(self.df_estoque_all.loc[i, 'Material No']) == f:

                    #test[str(self.df_estoque_all.loc[i, 'Material No'])] = self.df_estoque_all.loc[i]

                    if self.d[f].get("Description") == None:
                        self.d[f]['Description'] = self.df_estoque_all.loc[i, 'Material Description']


                    if self.d[f]['Batch'].get(str(self.df_estoque_all.loc[i, 'Batch'])) == None:
                        self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])] = {}
                    
                    if self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])].get('Stock Amount') == None:
                        self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Stock Amount'] = self.df_estoque_all.loc[i, 'Stock']
                    else:
                        self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Stock Amount'] += self.df_estoque_all.loc[i, 'Stock']
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Plant'] = str(self.df_estoque_all.loc[i, 'Plant'])
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Batch status key'] = str(self.df_estoque_all.loc[i, 'Batch status key'])

                    #Expiration date
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Shelf life'] = (self.df_estoque_all.loc[i, 'Expiration date'], self.df_estoque_all.loc[i, 'Expiration date'].strftime('%Y-%m-%d'))

                    #days (timedelta)
                    delta = str(date.today() - self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Shelf life'][0].date())
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Days'] = eval(delta[:delta.find(' days')]) if delta.find(' days') != -1 else eval(delta[:delta.find(' day')]) if delta.find(' day') != -1 else 0
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Month'] = float('{:.1f}'.format(eval(delta[:delta.find(' days')])/30)) if delta.find(' days') != -1 else float('{:.1f}'.format(eval(delta[:delta.find(' day')])/30)) if delta.find(' day') != -1 else 0

                    limit = self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Shelf life'][0].date() - timedelta(days=30*12)
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Limit sales date'] = (limit, limit.strftime('%Y-%m-%d'))


        #Planilha Forecast
        df = {}
        forecast = {}
        estoqueInicial = {}
        coberturaInicial = {}
        coberturaFinal = {}
        estoqueFinal = {}
        entrada ={}
        np_arr = np.random.rand(1,5)
        
        cols = list(self.df_forecast.columns)
        
        for key in list(self.d.keys()):
            df[key] = pd.DataFrame()
            estoqueInicial[key] = {}
            estoqueFinal[key] = {}
            coberturaFinal[key] = {}
            entrada[key] = {}

        
            for i in range(len(self.df_forecast)):
                if self.df_forecast.loc[i, 'Product Code'] == key:
                    temp_df = self.df_forecast.loc[i]

                    monthFlag = False
                    numCols = len(cols)
                    lim = 0
                    j = 0
                    for j in range(numCols):
                        if cols[j] == month and monthFlag == False:
                            monthFlag = True
                            if j + 6 <= numCols:
                                lim = j + 6
                            else:
                                lim = numCols
                            break

                    if monthFlag == True and j < lim:

                        forecast[key] = temp_df[cols[j:lim]]

                        indexes = list(forecast[key].index)

                        coberturaFinal_dict = {}
                        for idx in range(len(np_arr[0])):
                            coberturaFinal_dict[indexes[idx]] = np_arr[0][idx]/forecast[key][indexes[idx + 1]]
                        coberturaFinal[key] = pd.Series(coberturaFinal_dict, index=indexes)  
                                             
                        

                        tmp_dict = {}

                        for m in indexes[:-1]: 
                            tmp_dict[m] = coberturaFinal[key][m]

                        estoqueInicial[key] = pd.Series(data=tmp_dict, index=indexes)
                        entrada[key] = pd.Series(data=tmp_dict, index=indexes)


                        tmp_estoqueFinal = {}
                        tmp_estoqueFinal.setdefault(key, pd.Series(index=indexes[:-1]))

                        for m in indexes[:-1]: 

                            
                            
                            if m == month:
                                if self.d.get(key) != None:

                                    if forecast[key][m] > self.d[key].get('Colocado'):

                                        tmp_estoqueFinal[key][m] = estoqueInicial[key][m] + entrada[key][m] - forecast[key][m]
                                    else:
                                        tmp_estoqueFinal[key][m] = estoqueInicial[key][m] + entrada[key][m] - self.d[key]['Colocado']
                            else:
                                tmp_estoqueFinal[key][m] = estoqueInicial[key][m] + entrada[key][m] - forecast[key][m]

                        estoqueFinal[key] = pd.Series(data=tmp_estoqueFinal[key], index=indexes)


                    df[key]['month'] = indexes
                    df[key]['forecast'] = forecast[key].values
                    df[key]['Entrada'] = entrada[key].values
                    df[key]['EstoqueInicial'] = estoqueInicial[key].values
                    df[key]['EstoqueFinal'] = estoqueFinal[key].values
                    df[key]['CoberturaInicial'] = df[key].apply(lambda x: 0, axis = 1)
                    df[key]['CoberturaFinal'] = coberturaFinal[key].values
                    df[key]['EstoquePolitica'] = df[key].apply(lambda x: 0, axis = 1)
      

       
                    for i in range(len(df[key])):
                        try:
                            df[key].loc[i, 'CoberturaInicial'] = df[key].loc[i, 'EstoqueInicial'] / df[key].loc[i, 'forecast']
                        except:
                            pass

                        try:
                            df[key].loc[i, 'EstoquePolitica'] = df[key].loc[i, 'forecast'] + df[key].loc[i+1, 'forecast'] / 3
                        except:
                            pass       


                        
            #print(df[key].head())
        
        print(df)
        print()







x = Medicamentos(sheets)
x.calcular('JAN 2021', 39)