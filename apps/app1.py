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

layout = html.Div(children=[

    html.H1(children='Data Campfire Datathon', style={
        'textAlign': 'center',
    }),

    # Cruce 1

    html.H2(children='Cruce 1', style={
        'textAlign': 'center',
    }),

    dcc.Dropdown(
        id='categories-1',
        options=[{
            'label': i, 'value': i
        } for i in df_gastos['Partida'].unique()],
        value=df_gastos['Partida'].unique()[0]
    ),

    dcc.Graph(
        id='expenditure-vs-budget-by-year',
        clickData={'points': []}
    ),

    html.H4(id='expenditure-by-month-title', style={
        'textAlign': 'center'
    }),

    # Cruce 8

    html.H2(children='Cruce 8', style={
        'textAlign': 'center'
    }),

    dcc.Graph(
        id='pop-growth-vs'
    ),

    dcc.Graph(
        id='expenditure-by-month'
    )
])


@app.callback(
    Output('expenditure-vs-budget-by-year', 'figure'),
    [Input('categories-1', 'value')]
)
def updateExpVsBudgetChart(category):

    sub_df = df_gastos[(df_gastos['Partida'] == category)]

    traces = []

    BAR_TYPES = ['Gastos', 'Presupuesto']
    BAR_NAMES = ['Gastos', 'Presupuesto']

    for (cat, name) in zip(BAR_TYPES, BAR_NAMES):
        traces.append(
            go.Bar(
                x=sub_df['Periodo'],
                y=sub_df[cat],
                name=name
            )
        )

    return go.Figure(data=traces)


@app.callback(
    Output('expenditure-by-month', 'figure'),
    [
        Input('expenditure-vs-budget-by-year', 'clickData'),
        Input('categories-1', 'value')
    ]
)
def updateExpByMonthChart(clickData, category):

    sub_df = df_month[(df_month['Nombre Partida'] == category)]
    year = clickData['points'][0]['x']
    sub_df = sub_df[(sub_df['Periodo'] == year)]

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
    Output('expenditure-by-month-title', 'children'),
    [
        Input('expenditure-vs-budget-by-year', 'clickData'),
        Input('categories-1', 'value')
    ]
)
def updateExpByMonthChartTitle(clickData, category):

    if category is None:
        return ''

    year = clickData['points'][0]['x']

    return str(category) + ' - ' + str(year)
