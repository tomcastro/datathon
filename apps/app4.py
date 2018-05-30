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
    exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
    pib_path = os.path.join(current_path, 'datasets', 'dataset_5.csv')
else:
    base_url = 'http://uai-datathon-datasets.s3-accelerate.amazonaws.com/'
    month_path = base_url + 'datasets/dataset_1.csv'
    exp_path = base_url + 'datasets/dataset_2.csv'


# Get dataset 2, rename last column, group by year

df_gastos = pd.read_csv(exp_path, sep=';')
cols = df_gastos.columns.values
cols[-1] = 'Gastos'
cols[-2] = 'Presupuesto'
df_gastos.columns = cols

df_gb = df_gastos.groupby(['Periodo'])['Gastos', 'Presupuesto'].sum()

df_gastos = df_gb.reset_index()
df_gastos = df_gastos.sort_values(by=['Periodo'])

# Dataset 5

df_pib = pd.read_csv(pib_path, sep=';')
print(df_pib.head())
cols = df_pib.columns.values
cols[0] = 'Periodo'
cols[1] = 'PIB'
df_pib.columns = cols

df_pib = df_pib[(df_pib['Periodo'] >= 2009)]

layout = html.Div(children=[
    html.H1(children='Data Campfire Datathon', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='pib-vs-exp',
        figure={
            'data': [
                go.Scatter(
                    x=df_gastos['Periodo'],
                    y=df_gastos['Gastos'],
                    name='Gastos',
                    fill='tonexty'
                ),
                go.Scatter(
                    x=df_gastos['Periodo'],
                    y=df_gastos['Presupuesto'],
                    name='Presupuesto',
                    fill='tonexty'
                ),
                go.Scatter(
                    x=df_pib['Periodo'],
                    y=df_pib['PIB'],
                    name='PIB',
                    fill='tozeroy'
                )
            ]
        }
    )
])
