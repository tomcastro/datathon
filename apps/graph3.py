# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import random as r
import squarify as sq
from dash.dependencies import Input, Output

from app import app

# Get CSV files depending on environment

if 'ENV' in os.environ and os.environ['ENV'] == 'dev':
    current_path = os.getcwd()
    inc_path = os.path.join(current_path, 'datasets', 'dataset_3.csv')
    pib_path = os.path.join(current_path, 'datasets', 'dataset_5.csv')
else:
    base_url = 'http://uai-datathon-datasets.s3-accelerate.amazonaws.com/'
    month_path = base_url + 'datasets/dataset_1.csv'
    exp_path = base_url + 'datasets/dataset_2.csv'
    pop_path = base_url + 'datasets/dataset_4.csv'

# Get dataset 3

df_inc = pd.read_csv(inc_path, sep=';', encoding='latin1')
df_inc = df_inc[(df_inc['NIVEL1'] == 'TRANSACCIONES QUE AFECTAN EL PATRIMONIO NETO')]
df_inc['Real_amount'] = df_inc['Real_amount'].str.replace(',', '.')
df_inc['Real_amount'] = df_inc['Real_amount'].apply(pd.to_numeric)
df_exp = df_inc[(df_inc['NIVEL2'] == 'GASTOS')]
df_inc = df_inc[(df_inc['NIVEL2'] == 'INGRESOS')]
# print(df_inc)

# Get dataset 5

df_pib = pd.read_csv(pib_path, sep=';')
cols = df_pib.columns.values
cols[0] = 'Periodo'
cols[1] = 'PIB'
df_pib.columns = cols
df_pib = df_pib.reset_index(drop=True)
# df_pib['PIB'] = df_pib['PIB'].apply(lambda x: x*1000)

YEARS_INT = df_pib['Periodo'].unique()
YEARS_STR = [str(i) for i in YEARS_INT]

layout = html.Div(className='container', children=[

    html.H2(children='Ingreso y gasto vs. PIB', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='pie-charts'
    ),

    dcc.Slider(
        id='year-slider',
        included=False,
        min=min(YEARS_INT),
        max=max(YEARS_INT),
        marks={j: i for (i, j) in zip(YEARS_INT, YEARS_STR)},
        value=min(YEARS_INT)
    ),

    html.Div(className='graph', children=[
        dcc.Graph(
            id='treemap'
        )
    ])
])


@app.callback(
    Output('treemap', 'figure'),
    [
        Input('pie-charts', 'clickData'),
        Input('year-slider', 'value')
    ]
)
def updateTreemap(clickData, year):
    if clickData is None:
        return go.Figure(data=[])

    clickedGraph = clickData['points'][0]['curveNumber']

    if clickedGraph == 0:
        sub_df = df_inc[(df_inc['Periodo']) == year]
    elif clickedGraph == 1:
        sub_df = df_exp[(df_exp['Periodo']) == year]

    total = sub_df.groupby(['Periodo'], as_index=False)['Real_amount'].sum()
    total = total[0]['Real_amount']

    x, y = 0., 0.
    width, height = 100., 100.

    normed = sq.normalize_sizes(values, width, height)
    rects = sq.squarify(normed, x, y, width, height)

    return go.Figure(data=[])


@app.callback(
    Output('pie-charts', 'figure'),
    [Input('year-slider', 'value')]
)
def updatePieCharts(year):
    pib = df_pib[(df_pib['Periodo'] == year)].iloc[0]['PIB']
    print(df_inc[(df_inc['Periodo'] == year)].iloc[0]['Real_amount'])
    perc_inc = df_inc[(df_inc['Periodo'] == year)].iloc[0]['Real_amount'] * 100 / pib
    perc_exp = df_exp[(df_exp['Periodo'] == year)].iloc[0]['Real_amount'] * 100 / pib

    perc_pib_inc = 100 - perc_inc
    perc_pib_exp = 100 - perc_exp

    traces = []

    traces.append(go.Pie(
        labels=['PIB', 'Ingresos'],
        values=[perc_pib_inc, perc_inc],
        hoverinfo='label+percent',
        textinfo='value',
        domain={'x': [0, 0.48]},
        name='Ingresos',
        hole=0.4,
    ))

    traces.append(go.Pie(
        labels=['PIB', 'Gastos'],
        values=[perc_pib_exp, perc_exp],
        hoverinfo='label+percent',
        textinfo='value',
        domain={'x': [0.5, 1]},
        name='Gastos',
        hole=0.4,
    ))

    return go.Figure(data=traces)
