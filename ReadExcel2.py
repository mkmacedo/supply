from cmath import nan
from datetime import date, datetime, timedelta
import math
from operator import index
#from tracemalloc import start
#from matplotlib.pyplot import axes, axis
import pandas as pd
import regexes
import sys
import numpy as np
import re



filenames = sys.stdin.read()
print(filenames)

sheets = filenames.split('\n')


class Medicamentos:
    
    def __init__(self, sheets):

        self.df_vendas = pd.read_excel(sheets[0].strip())
        self.df_produtos = pd.read_excel(sheets[1].strip())
        self.df_estoque_blocked = pd.read_excel(sheets[2].strip())
        self.df_estoque_all = pd.read_excel(sheets[3].strip())
        self.df_forecast = pd.read_excel(sheets[4].strip())
        self.df_colocado = pd.read_excel(sheets[5].strip())
        self.df_biotech = pd.read_excel(sheets[6].strip())
        self.df_jda = pd.read_excel(sheets[7].strip())

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





        df = {} # Chave ==>> Código do Material; Valor ==>> DataFrame
        codes = list(self.d.keys())

        for key in codes:
            df[key] = pd.DataFrame()
        
        indexes = list(self.df_forecast.columns) # Lista de colunas da planilha Forecast
        JDA_Cols = list(self.df_jda.columns)

        #print(indexes)
        #print(JDA_Cols)

        beginning = 0
        limit = 0
        for i in range(len(indexes)):        
            if indexes[i] == month:
                beginning = i
                if beginning + 6 > len(indexes):
                    limit = len(indexes)
                else:
                    limit = beginning + 6

        for i in range(len(self.df_forecast)):

            code = self.df_forecast.loc[i, 'Product Code'] # Código do Material obtido da planilha Forecast

            if code in codes:

                forecast = self.df_forecast.loc[i]
   
                df[code]['Meses'] = indexes[beginning:limit]
                df[code]['Forecast'] = forecast[list(df[code]['Meses'])].values

                df[code]['Entrada'] = df[code].apply(lambda x: 0, axis = 1)
                
                #print(df[code])

        for i in range(len(self.df_jda)):
            code = self.df_jda.loc[i, 'Item']
            
            if code in codes:
                
                entrada = pd.Series(data=np.zeros((1,len(indexes[beginning:limit])))[0],index=indexes[beginning:limit])
                #print(entrada)

                startColumn = None
                for d in JDA_Cols[15:]:
                    r = re.search(r'[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]', d)
                    rStr = ''
                    if r != None:
                        rStr = r.group().replace(".", "/")
                        dateObj = datetime.strptime(rStr, "%d/%m/%y")
                        rStr = dateObj.strftime("%b %Y").upper()

                    if rStr == month:
                        startColumn = d 
                        break

                tempSeries = self.df_jda.loc[i]
                jdaBeginning = JDA_Cols.index(startColumn)
                jdaLimit = jdaBeginning + 6 if jdaBeginning + 6 < len(JDA_Cols) else len(JDA_Cols)
                tempSeries = tempSeries[JDA_Cols[jdaBeginning:jdaLimit]]
                #entrada = 
                #print(tempSeries.values)

                for index, m in enumerate(entrada):
                    #print(index,'-', m, '-', list(entrada.index)[index])
                    m_ = re.search(r'[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]', str(list(tempSeries.index)[index]))#.group()
                    if m_ != None:
                        m_ = m_.group().replace(".", "/")
                        dateObj_ = datetime.strptime(m_, "%d/%m/%y")
                        m_ = dateObj_.strftime("%b %Y").upper()
                        entrada[m_] = tempSeries[list(tempSeries.index)[index]]
                        #str(w).replace(',', '').isdigit()
                        #print(entrada(m_))
                #print(tempSeries)
                print(entrada)





#                monthFlag = False
#                numCols = len(cols)
#                lim = 0
#                j = 0
#                for j in range(numCols):
#                    if cols[j] == month and monthFlag == False:
#                        monthFlag = True
#                        if j + 6 <= numCols:
#                            lim = j + 6
#                        else:
#                            lim = numCols
#                        break
                



            #print(df[key].head())
        #print(df)



x = Medicamentos(sheets)
x.calcular('APR 2022', 39)