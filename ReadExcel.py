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
        print(self.df_colocado.head())
        self.df_biotech = pd.read_excel(sheets[6].strip())

        self.d = {}

    def calcular(self):

        material = self.df_estoque_all['Material No']
        material = material.unique()
        
        for f in material:

            self.d[f] = {}
            self.d[f]['Sales'] = 0
            self.d[f]['Delivery'] = ''
            self.d[f]['Colocado'] = 0
            self.d[f]['Batch'] = {}

            for i in range(len(self.df_vendas)):
                if str(self.df_vendas.loc[i, 'Material']) == f:
                    self.d[f]['Sales'] += self.df_vendas.loc[i, 'Quantity']

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
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Days'] = eval(delta[:delta.find(' days')])
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Month'] = float('{:.1f}'.format(eval(delta[:delta.find(' days')])/30))

                    limit = self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Shelf life'][0].date() - timedelta(days=30*12)
                    self.d[f]['Batch'][str(self.df_estoque_all.loc[i, 'Batch'])]['Limit sales date'] = (limit, limit.strftime('%Y-%m-%d'))
                    

                    
                        

#                    if self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])].get('Stock Amount') == None:
#                        self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Stock Amount'] = self.df_estoque_all.loc[i, 'Stock'] #number
#                    else:
#                        self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Stock Amount'] += self.df_estoque_all.loc[i, 'Stock'] #number
#                    self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Plant'] = str(self.df_estoque_all.loc[i, 'Plant'])
#                    self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Batch status key'] = str(self.df_estoque_all.loc[i, 'Batch status key'])
#
#                    #Expiration date
#                    self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Shelf life'] = (self.df_estoque_all.loc[i, 'Expiration date'], self.df_estoque_all.loc[i, 'Expiration date'].strftime('%Y-%m-%d'))
#                    
#                    #days (timedelta)
#                    delta = str(date.today() - self.d[f]['Shelf life'][0].date())
#                    self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Days'] = eval(delta[:delta.find(' days')])
#                    self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Month'] = float('{:.1f}'.format(eval(delta[:delta.find(' days')])/30))
#
#                    limit = self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Shelf life'][0].date() - timedelta(days=30*12)
#                    self.d[f][str(self.df_estoque_all.loc[i, 'Batch'])]['Limit sales date'] = (limit, limit.strftime('%Y-%m-%d'))
#         
#
#
#        for key in list(self.d.keys()):
#            for i in range(len(self.df_vendas)):
#                if self.df_vendas.loc[i, 'Material'] == key and self.df_vendas.loc[i, 'Batch'] in list(self.d[key].keys()):
#                    self.d[key][str(self.df_estoque_all.loc[i, 'Batch'])]['Quantity'] = self.df_vendas.loc[i, 'Quantity']
#                    #Sales::::
#                    self.d[key][str(self.df_estoque_all.loc[i, 'Batch'])]['Sales'] = self.d[key].get('Quantity')*(-1) #if self.d[key].get('Quantity') != None and str(self.d[key].get('Quantity')).replace('.', '').isdigit else nan
#
#            for i in range(len(self.df_colocado)) and self.df_vendas.loc[i, 'Batch'] in list(self.d[key].keys()):
#                if self.df_colocado.loc[i, 'Código'] == key:
#                    self.d[key]['Colocado'] = self.df_colocado.loc[i, 'Colocado']
#                    try:
#                        self.d[key]['Delivery'] = self.d[key]['Colocado'] - self.d[key]['Sales']
#                    except:
#                        if self.d[key].get('Sales') != None:
#                            self.d[key]['Delivery'] = self.d[key]['Sales']*(-1)


        




        #x = list(self.d.keys())
        #print(math.isnan(x[-1]))
        #print(math.isnan(x[-1]))
        #print(x[-1].isnan())
        print(self.d)

x = Medicamentos(sheets)
x.calcular()



#for i in range(len(self.df_vendas)):
#    for key in list(d.keys()):
#
#        if self.df_vendas.loc[i, 'Material'] == key:
#
#            if self.df_vendas.loc[i, 'Batch'] == self.d[key]['Batch']:
#                self.d[key]['Quantity'] = str(self.df_vendas.loc[i, 'Quantity']).replace('.', '')
#
#    for i in range(len(self.df_colocado)):
#        for key in list(d.keys()):
#            if self.df_colocado.loc[i, 'Código'] == key:
#                self.d[key]['Colocado'] = str(self.df_colocado.loc[i, 'Colocado']).replace('.', '')
#
#for key in list(d.keys()):
#
#    self.d[key]['Sales'] = eval(self.d[key].get('Quantity'))*(-1) if self.d[key].get('Quantity') != None and str(self.d[key].get('Quantity')).replace('.', '').isdigit else 0
#    if self.d[key].get('Colocado') != None and self.d[key].get('Colocado').isdigit():
#        self.d[key]['Delivery'] = eval(self.d[key]['Colocado']) - self.d[key]['Sales']
#    else:
#        self.d[key]['Delivery'] = self.d[key]['Sales']*(-1)
#    self.d[key]['Stock Amount'] = eval(self.d[key]['Stock'])/1000 if self.d[key].get('Stock') != None else '-'
#
#    if self.d[key].get('Expiration date') != None:
#
#        self.d[key]['Shelf life'] = datetime.strptime(str(self.d[key]['Expiration date']), '%Y-%m-%d')
#        self.d[key]['Days'] = date.today() - self.d[key]['Shelf life'].date()
#
#        self.d[key]['Month'] = int(str(self.d[key]['Days'])[:str(self.d[key]['Days']).find(' days')])/30
#
#        self.d[key]['Limit sales date'] = (self.d[key]['Shelf life'] - timedelta(30))



#print(d)


#    if str(f) == str(self.df_vendas.loc[i, 'Material']):
#        codigo_material = [(self.df_vendas.loc[i, 'Material'], self.df_vendas.loc[i, 'Material description'], self.df_vendas.loc[i, 'Quantity']) for i in range(len(self.df_vendas[['Material']]))]
#
#prod = {}
#for t in codigo_material:
#    t


#print(codigo_material)


#print(df_biotech.head())
