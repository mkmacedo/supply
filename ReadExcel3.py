from cmath import nan
from datetime import date, datetime, timedelta
from icecream import ic
import math
from operator import index
#from tracemalloc import start
#from matplotlib.pyplot import axes, axis
import pandas as pd
import regexes
import sys
import numpy as np
import re
import traceback



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
        drp = pd.ExcelFile(sheets[6].strip())
        self.df_drp = pd.read_excel(drp, 'DRP+SS')

        self.d = {}

    def calcular(self, month, eInicial=(None, None)):
        #print(self.df_drp[['*Item', 'SS (min)']])

        material = self.df_estoque_all['Material No']
        material = material.unique()

        #test = {}
        
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



            #Produtos (Linhas roxas)
            for i in range(len(self.df_produtos)):

                if str(self.df_produtos.loc[i, 'Código']) == f:

                    #test[str(self.df_estoque_all.loc[i, 'Material No'])] = self.df_estoque_all.loc[i]


                    if self.d[f]['Batch'].get(str(self.df_produtos.loc[i, 'Batch'])) == None:
                        if self.d[f].get('batchAbaProdutos') == None:
                            self.d[f]['batchAbaProdutos'] = {}

                        if self.d[f]['batchAbaProdutos'].get(str(self.df_produtos.loc[i, 'Batch'])) == None:
                            self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])] = {}
                    
                        if self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])].get('Stock Amount') == None:
                            self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Stock Amount'] = self.df_produtos.loc[i, 'Amount']
                        else:
                            self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Stock Amount'] += self.df_produtos.loc[i, 'Amount']
                        #print(self.df_produtos.loc[i, 'Amount'], self.d[f]['Batch'][str(self.df_produtos.loc[i, 'Batch'])]['Stock Amount'])
                        self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Plant'] = ''
                        self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Batch status key'] = ''

                        #Expiration date
                        self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Shelf life'] = (self.df_produtos.loc[i, 'Validade'], self.df_produtos.loc[i, 'Validade'].strftime('%Y-%m-%d'))

                        #days (timedelta)
                        delta = str(date.today() - self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Shelf life'][0].date())
                        self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Days'] = eval(delta[:delta.find(' days')]) if delta.find(' days') != -1 else eval(delta[:delta.find(' day')]) if delta.find(' day') != -1 else 0
                        self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Month'] = float('{:.1f}'.format(eval(delta[:delta.find(' days')])/30)) if delta.find(' days') != -1 else float('{:.1f}'.format(eval(delta[:delta.find(' day')])/30)) if delta.find(' day') != -1 else 0

                        limit = self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Shelf life'][0].date() - timedelta(days=30*12)
                        self.d[f]['batchAbaProdutos'][str(self.df_produtos.loc[i, 'Batch'])]['Limit sales date'] = (limit, limit.strftime('%Y-%m-%d'))





        df = {} # Chave ==>> Código do Material; Valor ==>> DataFrame
        codes = list(self.d.keys())

        for key in codes:
            df[key] = pd.DataFrame()
        
        indexes = list(self.df_forecast.columns) # Lista de colunas da planilha Forecast
        JDA_Cols = list(self.df_jda.columns)

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

                df[code]['Entrada'] = df[code].apply(lambda x: 0., axis = 1)

                df[code]['EstoqueInicial'] = df[code].apply(lambda x: 0., axis = 1)

                df[code]['EstoqueFinal'] = df[code].apply(lambda x: 0., axis = 1)

                df[code]['CoberturaInicial'] = df[code].apply(lambda x: '0.0%', axis = 1)

                df[code]['CoberturaFinal'] = df[code].apply(lambda x: '0.0%', axis = 1)

                df[code]['EstoquePolitica'] = df[code].apply(lambda x: '0.0', axis = 1)
                
                #print(df[code])

        for i in range(len(self.df_jda)):

            if self.df_jda.loc[i,'Projection Columns'] in ['CommitIntransIn', 'ActualIntransIn', 'RecArriv']:

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

                    for index, _ in enumerate(entrada):
                        #print(index,'-', m, '-', list(entrada.index)[index])
                        m = re.search(r'[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9]', str(list(tempSeries.index)[index]))#.group()
                        if m != None:
                            m = m.group().replace(".", "/")
                            dateObj_ = datetime.strptime(m, "%d/%m/%y")
                            m = dateObj_.strftime("%b %Y").upper()
                            entrada[m] = tempSeries[list(tempSeries.index)[index]]

                    #print(tempSeries)
                    #print(entrada)
                    for index, v in enumerate(df[code]['Entrada']):

                        val = str(entrada[list(entrada.index)[index]])
                        if val.replace(',', '').replace('.', '').replace('-', '').isdigit():
                            val = eval(val.replace(',', ''))

                        if type(val) == type(1.0) or type(val) == type(1):
                            
                            df[code].at[index,'Entrada'] += val
                        #print(df[code].at[index,'Entrada'])
                        #print(index,v)
                    #print(df[code])
        #print(df)

        for key in list(df.keys()): #Percorrendo DataFrames em df
            epFactor = 0 

            for j in range(len(self.df_drp)):
                if self.df_drp.at[j, '*Item'] == key:
                    try:
                        ss_value = self.df_drp.at[j, 'SS (min)']/30 - 1
                        epFactor = ss_value if ss_value > 0 else 0
                    except:
                        #traceback.print_exc()
                        pass

            #Aqui
            for k in range(len(self.df_estoque_blocked)):
                if self.df_estoque_blocked.loc[k, 'Material No'] == key:
                    try:
                        df[key].at[0, 'EstoqueInicial'] = self.df_estoque_blocked.loc[k, 'Stock']*(-1)
                    except:
                        ...
            
            for k in range(len(self.df_estoque_all)):
                if key == self.df_estoque_all.loc[k, 'Material No']:
                    #print(self.df_estoque_all.loc[k, 'Stock'])


                    #print(key)
                    for i in range(len(df[key])):
                        
                        if i == 0:# and eInicial[0] == key:
                            if self.d.get(key) != None:# and eInicial[0] == key:
                                df[key].at[i, 'EstoqueInicial'] += self.df_estoque_all.loc[k, 'Stock']#eInicial[1]
                                if df[key].at[i, 'Forecast'] > self.d[key].get('Colocado'):
                                    df[key].at[i, 'EstoqueFinal'] = df[key].at[i, 'EstoqueInicial'] + df[key].at[i, 'Entrada'] - df[key].at[i, 'Forecast']
                                else:
                                    df[key].at[i, 'EstoqueFinal'] = df[key].at[i, 'EstoqueInicial'] + df[key].at[i, 'Entrada'] - self.d[key].get('Colocado')

                                try:
                                    df[key].at[i, 'CoberturaInicial'] =  '{:.2%}'.format(eInicial[1]/df[key].at[i, 'Forecast'])       
                                except:
                                    pass
                                
                                try:
                                    df[key].at[i, 'CoberturaFinal'] = '{:.2%}'.format(df[key].at[i, 'EstoqueFinal'] / df[key].at[i+1, 'Forecast'])

                                except:
                                    pass

                                try:
                                    df[key].at[i, 'EstoquePolitica'] = df[key].at[i, 'Forecast'] + df[key].at[i + 1, 'Forecast']*epFactor
                                except:
                                    pass
                                
                        elif eInicial[0] == key or eInicial[0] != None:

                            try:
                                df[key].at[i, 'EstoqueInicial'] = df[key].at[i - 1, 'EstoqueFinal'] #mudar
                                df[key].at[i, 'EstoqueFinal'] = df[key].at[i, 'EstoqueInicial'] + df[key].at[i, 'Entrada'] - df[key].at[i, 'Forecast']
                            except:
                                pass

                            try:
                                df[key].at[i, 'CoberturaInicial'] =  '{:.2%}'.format(df[key].at[i, 'EstoqueInicial']/df[key].at[i, 'Forecast'])
                            except:
                                pass

                            try:
                                df[key].at[i, 'CoberturaFinal'] = '{:.2%}'.format(df[key].at[i, 'EstoqueFinal'] / df[key].at[i+1, 'Forecast'])
                            except:
                                pass
                            
                            try:
                                df[key].at[i, 'EstoquePolitica'] = df[key].at[i, 'Forecast'] + df[key].at[i + 1, 'Forecast']*epFactor
                            except:
                                pass
            


            #print(key)
            #print(df[key])
            #print(df[key][['Forecast', 'EstoqueInicial', 'CoberturaInicial']])
            #print(self.d)
            for key in list(self.d.keys()):
                print(key, '--', self.d[key])
                print()
                print()
            
            #FN151201
            #F75D1201
            #FN131201

            #print(df[key].head())
        #print(df)



x = Medicamentos(sheets)
x.calcular('APR 2022', ('FN151201', 39))
