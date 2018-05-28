# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output

from app import app

# Get CSV files depending on environment

if 'ENV' in os.environ and os.environ['ENV'] == 'dev':
    current_path = os.getcwd()
    month_path = os.path.join(current_path, 'datasets', 'dataset_1.csv')
    exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
    inc_path = os.path.join(current_path, 'datasets', 'dataset_3.csv')
else:
    base_url = 'http://uai-datathon-datasets.s3-accelerate.amazonaws.com/'
    month_path = base_url + 'datasets/dataset_1.csv'
    exp_path = base_url + 'datasets/dataset_2.csv'
    pop_path = base_url + 'datasets/dataset_4.csv'


# Get dataset 2, rename last column, group by year

df_gastos = pd.read_csv(exp_path, sep=';')
cols = df_gastos.columns.values
cols[-1] = 'Gastos'
cols[-2] = 'Presupuesto'
df_gastos.columns = cols

df_gb = df_gastos.groupby(['Periodo'])['Gastos', 'Presupuesto'].sum()

df_gastos = df_gb.reset_index()
df_gastos = df_gastos.sort_values(by=['Periodo'])
# print(df_gastos.head())

# Dataset 3

df_inc = pd.read_csv(inc_path, sep=';', encoding='latin1')
df_inc = df_inc[(df_inc['Periodo'] >= 2009)]
df_inc['Real_amount'] = df_inc['Real_amount'].str.replace(',', '.')
df_inc['Real_amount'] = df_inc['Real_amount'].apply(pd.to_numeric)
df_gb = df_inc.groupby(['Periodo'])['Real_amount'].sum()
df_inc = df_gb.reset_index()
df_inc = df_inc.sort_values(by=['Periodo'])
# print(df_inc.head())



layout = html.Div(children=[
])
