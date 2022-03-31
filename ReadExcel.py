from cmath import nan
from datetime import date, datetime, timedelta
import math
import pandas as pd
import regexes
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
        forecast = {}
        coberturaInicial = {}
        cols = list(self.df_forecast.columns)
        
        for key in list(self.d.keys()):
            forecast[key] = {}
        
            for i in range(len(self.df_forecast)):
                if self.df_forecast.loc[i, 'Product Code'] == key:
                    temp_df = self.df_forecast.loc[i]
                    #print(temp_df)
#                    #print(self.df_forecast.loc[i, col_input])
#                    tables[key]['forecast'][month] = self.df_forecast.loc[i, month]
#                    tables[key]['forecast'][month] = self.df_forecast.loc[[key], month]
#
#                    break

            #print(self.df_forecast.loc[i, col_input])
                    monthFlag = False
                    numCols = len(cols)
                    lim = 0
                    j = 0
                    for j in range(numCols):
                        if cols[j] == month and monthFlag == False:
                            monthFlag = True
                            if j + 5 <= numCols:
                                lim = j + 5
                            else:
                                lim = numCols
                            break

                    if monthFlag == True and j < lim:
                        #forecast[key][cols[j]] = self.df_forecast.loc[i, cols[j]]
                        #temp_df = self.df_forecast.loc[i]
                        #print(temp_df[cols[j:lim]])#.values)
                        #print(cols)
                        #forecast[key]= self.df_forecast.loc[i, cols[j:lim]]
                        forecast[key]= temp_df[cols[j:lim]]
                        cInicial = []
                        for v in forecast[key]:
                            if len(cInicial) == 0:
                                cInicial.append(estoque_inicial/v)
                            else:
                                cInicial.append(cInicial[-1]/v)
                        print(cInicial)

            
            #print(forecast[key])

        print()
#        for key in list(test.keys()):
#            print(test[key][['Batch', 'Plant']])#.values)
#            print()
        #print(test)
        #print(forecast)
        #print(forecast['F1231201']['JAN 2021'])

        for i in forecast['F1231201']:
            print(i)

        #Estoque Inicial









        #x = list(self.d.keys())
        #print(math.isnan(x[-1]))
        #print(math.isnan(x[-1]))
        #print(x[-1].isnan())
        #print(self.d)

x = Medicamentos(sheets)
x.calcular('JAN 2021', 39)


#print(codigo_material)


#print(df_biotech.head())
