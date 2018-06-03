# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import squarify as sq
from dash.dependencies import Input, Output

from app import app

# Get CSV files depending on environment

current_path = os.getcwd()
exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
pib_path = os.path.join(current_path, 'datasets', 'dataset_5.csv')

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

# Get dataset 5

df_pib = pd.read_csv(pib_path, sep=';')
cols = df_pib.columns.values
cols[0] = 'Periodo'
cols[1] = 'PIB'
df_pib.columns = cols
df_pib = df_pib.reset_index(drop=True)
df_pib = df_pib[(df_pib['Periodo']) >= 2009].sort_values(['Periodo'])

YEARS_INT = df_pib['Periodo'].unique()
YEARS_STR = [str(i) for i in YEARS_INT]

layout = html.Div(className='container-fluid graph', children=[

    html.H2(children='Presupuesto y gasto vs. PIB', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='pie-charts-2',
        animate=True
    ),

    dcc.Slider(
        id='year-slider-2',
        included=False,
        min=min(YEARS_INT),
        max=max(YEARS_INT),
        marks={j: i for (i, j) in zip(YEARS_INT, YEARS_STR)},
        value=min(YEARS_INT)
    ),

    html.Div(className='graph', children=[
        html.H2(id='subtitle-2', style={'textAlign': 'center'}),

        dcc.Graph(
            id='treemap-2'
        )
    ])
])


@app.callback(
    Output('subtitle-2', 'children'),
    [
        Input('pie-charts-2', 'clickData'),
        Input('year-slider-2', 'value')
    ]
)
def updateSubtitle(clickData, year):
    if clickData is not None:
        clickedGraph = clickData['points'][0]['curveNumber']
    else:
        clickedGraph = 0

    string = 'Porcentaje de '

    if clickedGraph == 0:
        string += 'Presupuesto'
    elif clickedGraph == 1:
        string += 'Gastos'

    string += ' - ' + str(year)

    return [string]


@app.callback(
    Output('treemap-2', 'figure'),
    [
        Input('pie-charts-2', 'clickData'),
        Input('year-slider-2', 'value')
    ]
)
def updateTreemap(clickData, year):
    if clickData is not None:
        clickedGraph = clickData['points'][0]['curveNumber']
    else:
        clickedGraph = 0

    if clickedGraph == 0:
        sub_df = df_gastos[(df_gastos['Periodo']) == year]
        cat = 'Presupuesto'
    elif clickedGraph == 1:
        sub_df = df_gastos[(df_gastos['Periodo']) == year]
        cat = 'Gastos'

    total = sub_df.groupby(['Periodo'], as_index=False)[cat].sum()
    total = total.iloc[0][cat]

    x, y = 0., 0.
    width, height = 200., 100.

    normed = sq.normalize_sizes(sub_df[cat], width, height)
    rects = sq.squarify(normed, x, y, width, height)

    color_brewer = ['rgb(166,206,227)', 'rgb(31,120,180)', 'rgb(178,223,138)',
                    'rgb(51,160,44)', 'rgb(251,154,153)', 'rgb(227,26,28)',
                    'rgb(137,45,89)']

    shapes = []
    annotations = []
    counter = 0
    df_counter = 0

    for r in rects:
        shapes.append(dict(
            type='rect',
            x0=r['x'],
            y0=r['y'],
            x1=r['x']+r['dx'],
            y1=r['y']+r['dy'],
            line=dict(width=2),
            fillcolor=color_brewer[counter]
        ))

        if r['dx'] < 20 or r['dy'] < 20:
            text = ''
        else:
            text = sub_df.iloc[df_counter]['Partida'].replace(' ', '<br>')

        annotations.append(dict(
            x=r['x']+(r['dx']/2),
            y=r['y']+(r['dy']/2),
            text=text,
            showarrow=False,
            font=dict(size=10, color='#000000')
        ))

        counter += 1
        df_counter += 1
        if counter >= len(color_brewer):
            counter = 0

    trace = go.Scatter(
        x=[r['x']+(r['dx']/2) for r in rects],
        y=[r['y']+(r['dy']/2) for r in rects],
        text=[
            str(row['Partida']) + '<br>' +
            str(round(row[cat] / total * 100, 2)) +
            '%' for (i, row) in sub_df.iterrows()
        ],
        customdata=[],
        hoverinfo='text',
        textfont=dict(size=2),
        mode='text',
    )

    layout = dict(
        height=700,
        width=1700,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        shapes=shapes,
        annotations=annotations,
        hovermode='closest'
    )

    return go.Figure(data=[trace], layout=layout)


@app.callback(
    Output('pie-charts-2', 'figure'),
    [Input('year-slider-2', 'value')]
)
def updatePieCharts(year):
    pib = df_pib[(df_pib['Periodo'] == year)].iloc[0]['PIB']
    perc_bud = df_gastos[
        (df_gastos['Periodo'] == year)
    ].iloc[0]['Presupuesto'] * 100 / pib
    perc_exp = df_gastos[
        (df_gastos['Periodo'] == year)
    ].iloc[0]['Gastos'] * 100 / pib

    perc_pib_bud = 100 - perc_bud
    perc_pib_exp = 100 - perc_exp

    traces = []

    traces.append(go.Pie(
        labels=['PIB', 'Presupuesto'],
        values=[perc_pib_bud, perc_bud],
        hoverinfo='label+percent',
        textinfo='label',
        domain={'x': [0, 0.48]},
        name='Presupuesto',
        hole=0.4,
    ))

    traces.append(go.Pie(
        labels=['PIB', 'Gastos'],
        values=[perc_pib_exp, perc_exp],
        hoverinfo='label+percent',
        textinfo='label',
        domain={'x': [0.5, 1]},
        name='Gastos',
        hole=0.4,
    ))

    return go.Figure(data=traces)
