# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from dash.dependencies import Input, Output

from app import app

# Get CSV files depending on environment

current_path = os.getcwd()
month_path = os.path.join(current_path, 'datasets', 'dataset_1.csv')
exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
pop_path = os.path.join(current_path, 'datasets', 'dataset_4.csv')
imm_path = os.path.join(current_path, 'datasets',
                        'immigration_data', 'visas.csv')

# Get dataset 1

sorter = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

df_month = pd.read_csv(month_path, sep=';',
                       dtype={'Periodo': int, 'Monto_sum': int},
                       low_memory=False, encoding='utf-8')
df_gb = df_month.groupby(['Nombre Partida', 'Periodo', 'Mes'])['Monto_sum'] \
        .sum()
df_month = df_gb.reset_index()

df_month.Mes = df_month.Mes.astype('category')
df_month.Mes.cat.set_categories(sorter, inplace=True)
df_month = df_month.sort_values(['Nombre Partida', 'Periodo', 'Mes'])

df_month['Nombre Partida'] = df_month['Nombre Partida'].str.upper()

df_month['Nombre Partida'] = df_month['Nombre Partida'] \
                               .str.replace('Ó', 'O')
df_month['Nombre Partida'] = df_month['Nombre Partida'] \
                               .str.replace('Á', 'A')
df_month['Nombre Partida'] = df_month['Nombre Partida'] \
                               .str.replace('É', 'E')
df_month['Nombre Partida'] = df_month['Nombre Partida'] \
                               .str.replace('Í', 'I')
df_month['Nombre Partida'] = df_month['Nombre Partida'] \
                               .str.replace('Ú', 'U')

# Get dataset 2, rename last column, group by category and year

df_gastos = pd.read_csv(exp_path, sep=';', encoding='utf-8')
cols = df_gastos.columns.values
cols[-1] = 'Gastos'
cols[-2] = 'Presupuesto'
df_gastos.columns = cols

df_gb = df_gastos.groupby(['Partida', 'Periodo'])['Gastos', 'Presupuesto'] \
                 .sum()

df_gastos = df_gb.reset_index()

df_gastos['Partida'] = df_gastos['Partida'].str.upper()
df_gastos['Partida'] = df_gastos['Partida'] \
                        .str.replace('Ó', 'O')
df_gastos['Partida'] = df_gastos['Partida'] \
                        .str.replace('Á', 'A')
df_gastos['Partida'] = df_gastos['Partida'] \
                        .str.replace('É', 'E')
df_gastos['Partida'] = df_gastos['Partida'] \
                        .str.replace('Í', 'I')
df_gastos['Partida'] = df_gastos['Partida'] \
                        .str.replace('Ú', 'U')

# fix accent errors
df_gastos['Partida'] = df_gastos['Partida'].str.replace('Ê', 'I')
df_gastos['Partida'] = df_gastos['Partida'].str.replace('Ƒ', 'E')

CATEGORIES = df_gastos['Partida'].unique()
YEARS_INT = df_gastos['Periodo'].unique()
YEARS_STR = [str(i) for i in YEARS_INT]
COLORS = ['rgb(151,113,8)', 'rgb(235,172,2)', 'rgb(186,139,11)',
          'rgb(105,77,0)', 'rgb( 62, 46,0)', 'rgb(151,82,8)',
          'rgb(235,123,2)', 'rgb(186,102,11)', 'rgb(105,55,0)',
          'rgb(62,32,0)', 'rgb(9,71,95)', 'rgb(7,108,147)',
          'rgb(12,88,117)', 'rgb(3,49,66)', 'rgb(2,29,39)']

colors_assigned = {}
counter = 0
for category in df_month['Nombre Partida'].unique():
    colors_assigned[category] = COLORS[counter]
    counter += 1

    if counter == len(COLORS) - 1:
        counter = 0

layout = html.Div(className='container graph', children=[

    html.H2(children='Presupuesto vs. Gasto', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='bubble-budget-by-exp',
        # animate=True
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

        html.H2(id='subtitle-1', style={'textAlign': 'center'}),

        dcc.Graph(
            id='exp-by-month',
            # animate=True
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
    Output('subtitle-1', 'children'),
    [
        Input('year-slider', 'value'),
        Input('bubble-budget-by-exp', 'clickData')
    ]
)
def updateSubtitle(year, clickData):
    if clickData is None:
        category = CATEGORIES[0]
    else:
        category = clickData['points'][0]['text'].upper()

    string = category.title() + ' - ' + str(year)

    return [string]


@app.callback(
    Output('exp-by-month', 'figure'),
    [
        Input('bubble-budget-by-exp', 'clickData'),
        Input('year-slider', 'value')
    ]
)
def updateExpChart(clickData, year):
    if clickData is None:
        category = CATEGORIES[0]
    else:
        category = clickData['points'][0]['text'].upper()
    sub_df = df_month[(df_month['Periodo'] == year)]
    sub_df = sub_df[(sub_df['Nombre Partida'] == category)]

    traces = []

    traces.append(
        go.Scatter(
            x=sub_df['Mes'],
            y=sub_df['Monto_sum'],
            name=sub_df['Mes'],
            marker=dict(
                color=(colors_assigned[category]),
                size=9,
                opacity=1
            ),
            line=dict(
                color=(colors_assigned[category]),
                width=3
            )
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

    bubble_colors = []
    for i, row in sub_df.iterrows():
        bubble_colors.append(colors_assigned[row['Partida']])

    size = [(row['Gastos'] * row['Presupuesto'] / 1000000000)
            for i, row in sub_df.iterrows()]

    l, u = 0.05, 1
    scaled_size = normalize(
        size,
        {'actual': {'lower': min(size), 'upper': max(size)},
         'desired': {'lower': l, 'upper': u}}
    )
    scaled_size = [round(x*150) for x in scaled_size]

    traces = []

    traces.append(go.Scatter(
        x=sub_df['Gastos'],
        y=sub_df['Presupuesto'],
        name=sub_df['Partida'],
        text=[
            '{}'.format(row['Partida'].title())
            for i, row in sub_df.iterrows()
        ],
        mode='markers',
        marker=dict(
            size=scaled_size,
            color=bubble_colors,
            sizemode='diameter',
            sizemin=5
        )
    ))

    layout = go.Layout(
        xaxis=dict(title='Gastos (millones de pesos)'),
        yaxis=dict(title='Presupuesto (millones de pesos)'),
    )

    return go.Figure(data=traces, layout=layout)
