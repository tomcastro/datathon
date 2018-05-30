# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import random as r
from dash.dependencies import Input, Output

from app import app

# Get CSV files depending on environment

if 'ENV' in os.environ and os.environ['ENV'] == 'dev':
    current_path = os.getcwd()
    month_path = os.path.join(current_path, 'datasets', 'dataset_1.csv')
    exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
    pop_path = os.path.join(current_path, 'datasets', 'dataset_4.csv')
    imm_path = os.path.join(current_path, 'datasets',
                            'immigration_data', 'visas.csv')
else:
    base_url = 'http://uai-datathon-datasets.s3-accelerate.amazonaws.com/'
    month_path = base_url + 'datasets/dataset_1.csv'
    exp_path = base_url + 'datasets/dataset_2.csv'
    pop_path = base_url + 'datasets/dataset_4.csv'

# Get dataset 1

sorter = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

df_month = pd.read_csv(month_path, sep=';', dtype={'Periodo': int, 'Monto_sum': int}, low_memory=False)
df_gb = df_month.groupby(['Nombre Partida', 'Periodo', 'Mes'])['Monto_sum'] \
        .sum()
df_month = df_gb.reset_index()

df_month.Mes = df_month.Mes.astype('category')
df_month.Mes.cat.set_categories(sorter, inplace=True)
df_month = df_month.sort_values(['Nombre Partida', 'Periodo', 'Mes'])

df_month['Nombre Partida'] = df_month['Nombre Partida'].str.upper()

# Get dataset 2, rename last column, group by category and year

df_gastos = pd.read_csv(exp_path, sep=';')
cols = df_gastos.columns.values
cols[-1] = 'Gastos'
cols[-2] = 'Presupuesto'
df_gastos.columns = cols

df_gb = df_gastos.groupby(['Partida', 'Periodo'])['Gastos', 'Presupuesto'] \
                 .sum()

df_gastos = df_gb.reset_index()

CATEGORIES = df_gastos['Partida'].unique()
YEARS_INT = df_gastos['Periodo'].unique()
YEARS_STR = [str(i) for i in YEARS_INT]

layout = html.Div(className='container', children=[

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
            id='bubble-budget-by-exp'
        ),

        dcc.Graph(
            id='exp-by-month'
        )
    ])
])


def normalize(values, bounds):
    return [bounds['desired']['lower'] +
            (x - bounds['actual']['lower']) *
            (bounds['desired']['upper'] - bounds['desired']['lower']) /
            (bounds['actual']['upper'] - bounds['actual']['lower'])
            for x in values]


@app.callback(
    Output('exp-by-month', 'figure'),
    [
        Input('bubble-budget-by-exp', 'clickData'),
        Input('year-slider', 'value')
    ]
)
def updateExpChart(clickData, year):
    category = clickData['points'][0]['text'].upper()
    sub_df = df_month[(df_month['Periodo'] == year)]
    sub_df = sub_df[(sub_df['Nombre Partida'] == category)]

    traces = []

    traces.append(
        go.Scatter(
            x=sub_df['Mes'],
            y=sub_df['Monto_sum'],
            name=sub_df['Mes']
        )
    )

    return go.Figure(data=traces)


@app.callback(
    Output('bubble-budget-by-exp', 'figure'),
    [Input('year-slider', 'value')]
)
def updateBubbleChart(year):

    sub_df = df_gastos[(df_gastos['Periodo'] == year)]
    sub_df = sub_df.reset_index(drop=True)

    size = [(row['Gastos'] * row['Presupuesto'] / 1000000000)
            for i, row in sub_df.iterrows()]

    # scaled_size = [(x-min(size))/(max(size)-min(size))*100 for x in size]
    # print(scaled_size)

    colors = ['rgb({}, {}, {})'.format(r.randint(0, 256), r.randint(0, 256), r.randint(0, 256))
              for i, row in sub_df.iterrows()]

    l, u = 0.05, 1
    scaled_size = normalize(size,
        {'actual': {'lower': min(size), 'upper': max(size)}, 'desired': {'lower': l, 'upper': u}}
    )
    scaled_size = [round(x*150) for x in scaled_size]

    traces = []

    traces.append(go.Scatter(
        x=sub_df['Gastos'],
        y=sub_df['Presupuesto'],
        name=sub_df['Partida'],
        text=['{}'.format(row['Partida'].title()) for i, row in sub_df.iterrows()],
        mode='markers',
        marker=dict(
            size=scaled_size,
            color=colors,
            sizemode='diameter',
            sizemin=5
        )
    ))

    return go.Figure(data=traces)
