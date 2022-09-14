# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 08:08:21 2022

@author: eduardo.scheffer
"""

import pandas as pd
import pyodbc
import datetime as dt

def benchmark_prices_database(benchmark_list, date_first, date_last):

    ''' 1) SET UP DATA BASE CONNECTOR ----------------------------------------------------------------------------'''

    server = 'bswm-db.database.windows.net'
    database = 'bswm'
    username = 'bswm-sa'
    password = 'BatataPalha123!'   
    driver= '{ODBC Driver 18 for SQL Server}'
    
    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+',1433;Database='+database+';Uid='+username+';Pwd='+ password)
    
    
    ''' 2) IMPORT FUND PRICES --------------------------------------------------------------------------------------'''
    
    
    indices = pd.read_sql_query("SELECT * FROM Tbl_Indices", con=conn)
    values_index = pd.read_sql_query("SELECT * FROM Tbl_IndicesValores ORDER BY DtRef ASC", con=conn)
        
    dict_map = dict(zip(indices['IdIndice'], indices['NomeIndice']))
    
    values_index = values_index.pivot(index = 'DtRef', columns ='IdIndice' , values = 'Valor')
    
    #-30 to get the IPCA since the first date (monthly data) - these dates will be deleted after obtaining daily IPCA rates
    date_first = date_first-dt.timedelta(days=30)
    values_index = values_index[((values_index.index >= date_first) & (values_index.index <= date_last))]
    
    # Change IdIndice for index name
    benchmark_names = list(values_index.columns)
    benchmark_names = [dict_map.get(item, item) for item in benchmark_names]
    values_index.columns = benchmark_names
    
    # Filter only funds needed
    values_index = values_index.loc[:,values_index.columns.isin(benchmark_list)]
    
    return values_index