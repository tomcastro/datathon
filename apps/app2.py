# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output, State

from app import app

# Get CSV files depending on environment

if 'ENV' in os.environ and os.environ['ENV'] == 'dev':
    current_path = os.getcwd()
    month_path = os.path.join(current_path, 'datasets', 'dataset_1.csv')
    exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
else:
    base_url = 'http://uai-datathon-datasets.s3-accelerate.amazonaws.com/'
    month_path = base_url + 'datasets/dataset_1.csv'
    exp_path = base_url + 'datasets/dataset_2.csv'

# Get dataset 1

sorter = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

df_month = pd.read_csv(month_path, sep=';', dtype={'Periodo': int, 'Monto_sum': int}, low_memory=False)
df_gb = df_month.groupby(['Nombre Partida', 'Nombre Subtitulo', 'Periodo', 'Mes'])['Monto_sum'] \
        .sum()
df_month = df_gb.reset_index()

df_month.Mes = df_month.Mes.astype('category')
df_month.Mes.cat.set_categories(sorter, inplace=True)
df_month = df_month.sort_values(['Nombre Partida', 'Nombre Subtitulo', 'Periodo', 'Mes'])

df_month['Nombre Partida'] = df_month['Nombre Partida'].str.upper()
df_month['Nombre Subtitulo'] = df_month['Nombre Subtitulo'] \
                               .str.replace('Ó', 'O')
df_month['Nombre Subtitulo'] = df_month['Nombre Subtitulo'] \
                               .str.replace('Á', 'A')
df_month['Nombre Subtitulo'] = df_month['Nombre Subtitulo'] \
                               .str.replace('É', 'E')
df_month['Nombre Subtitulo'] = df_month['Nombre Subtitulo'] \
                               .str.replace('Í', 'I')
df_month['Nombre Subtitulo'] = df_month['Nombre Subtitulo'] \
                               .str.replace('Ú', 'U')


# Get dataset 2, rename last column, group by category and year

df_gastos = pd.read_csv(exp_path, sep=';')
df_gastos['SUBTÍTULO'] = df_gastos['SUBTÍTULO'].astype(str)
df_gastos['SUBTÍTULO'] = df_gastos['SUBTÍTULO'].map(lambda x: x.strip())
EXP_CATEGORIES = df_gastos['SUBTÍTULO'].unique()
cols = df_gastos.columns.values
cols[-1] = 'Gastos'
cols[-2] = 'Presupuesto'
df_gastos.columns = cols

df_gb = df_gastos.groupby(['Partida', 'SUBTÍTULO', 'Periodo'])['Gastos', 'Presupuesto'] \
                 .sum()

df_gastos = df_gb.reset_index()

CATEGORIES = df_gastos['Partida'].unique()

LAYOUT = go.Layout(xaxis=dict(range=[2009, 2017]))

layout = html.Div(children=[
    html.H1(children='Data Campfire Datathon', style={
        'textAlign': 'center',
    }),

    dcc.Dropdown(
        id='categories-2',
        options=[{
            'label': i, 'value': i
        } for i in CATEGORIES],
        value=CATEGORIES[0]
    ),

    dcc.Dropdown(
        id='subcategories-2',
        options=[],
        value=''
    ),

    dcc.Graph(
        id='exp-by-category-year'
    ),

    dcc.Graph(
        id='exp-by-category-month'
    )
])


@app.callback(
    Output('subcategories-2', 'options'),
    [Input('categories-2', 'value')]
)
def updateDropdown(category):
    if category is None:
        return []

    sub_df = df_gastos[(df_gastos['Partida'] == category)]

    options = []

    for sub in sub_df['SUBTÍTULO'].unique():
        options.append({'label': sub, 'value': sub})

    return options


@app.callback(
    Output('subcategories-2', 'value'),
    [Input('categories-2', 'value')]
)
def clearDropdown(category):
    return []


@app.callback(
    Output('exp-by-category-year', 'figure'),
    [Input('subcategories-2', 'value')],
    [State('categories-2', 'value')]
)
def updateExpByCategoryChart(subcategory, category):
    if not category or not subcategory:
        return go.Figure(data=[], layout=LAYOUT)

    sub_df = df_gastos[(df_gastos['Partida'] == category)]
    sub_df = sub_df[(sub_df['SUBTÍTULO'] == subcategory)]

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
    Output('exp-by-category-month', 'figure'),
    [
        Input('exp-by-category-year', 'clickData'),
        Input('categories-2', 'value'),
        Input('subcategories-2', 'value')
    ]
)
def updateExpByCategoryMonthlyChart(clickData, category, subcategory):
    if not category or not subcategory:
        return go.Figure(data=[])

    year = clickData['points'][0]['x']

    sub_df = df_month[(df_month['Periodo'] == year) &
                      (df_month['Nombre Partida'] == category) &
                      (df_month['Nombre Subtitulo'] == subcategory)]

    traces = []

    traces.append(
        go.Scatter(
            x=sub_df['Mes'],
            y=sub_df['Monto_sum'],
            name=sub_df['Mes']
        )
    )

    return go.Figure(data=traces)
