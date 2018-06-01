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
inc_path = os.path.join(current_path, 'datasets', 'dataset_3.csv')
pib_path = os.path.join(current_path, 'datasets', 'dataset_5.csv')

# Get dataset 3

df_inc = pd.read_csv(inc_path, sep=';', encoding='latin1')
df_inc = df_inc[(df_inc['NIVEL1'] == 'TRANSACCIONES QUE AFECTAN EL PATRIMONIO NETO')]
df_inc['Real_amount'] = df_inc['Real_amount'].str.replace(',', '.')
df_inc['Real_amount'] = df_inc['Real_amount'].apply(pd.to_numeric)
df_exp = df_inc[(df_inc['NIVEL2'] == 'GASTOS')].reset_index(drop=True)
df_exp = df_exp.sort_values(['Periodo', 'NIVEL1', 'NIVEL2', 'NIVEL3'])
df_inc = df_inc[(df_inc['NIVEL2'] == 'INGRESOS')].reset_index(drop=True)
df_inc = df_inc.sort_values(['Periodo', 'NIVEL1', 'NIVEL2', 'NIVEL3'])
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
        html.H2(id='subtitle', style={'textAlign': 'center'}),

        dcc.Graph(
            id='treemap'
        )
    ])
])


@app.callback(
    Output('subtitle', 'children'),
    [
        Input('pie-charts', 'clickData'),
        Input('year-slider', 'value')
    ]
)
def updateSubtitle(clickData, year):
    if clickData is not None:
        clickedGraph = clickData['points'][0]['curveNumber']
    else:
        clickedGraph = 0

    string = 'Porcentaje de '

    if clickedGraph == 0:
        string += 'Ingresos'
    elif clickedGraph == 1:
        string += 'Gastos'

    string += ' - ' + str(year)

    return [string]


@app.callback(
    Output('treemap', 'figure'),
    [
        Input('pie-charts', 'clickData'),
        Input('year-slider', 'value')
    ]
)
def updateTreemap(clickData, year):
    if clickData is not None:
        clickedGraph = clickData['points'][0]['curveNumber']
    else:
        clickedGraph = 0

    if clickedGraph == 0:
        sub_df = df_inc[(df_inc['Periodo']) == year]
        sub_df_gb = sub_df.groupby(['Periodo', 'NIVEL3'])['Real_amount'].sum()
        sub_df = sub_df_gb.reset_index()
    elif clickedGraph == 1:
        sub_df = df_exp[(df_exp['Periodo']) == year]
        sub_df_gb = sub_df.groupby(['Periodo', 'NIVEL3'])['Real_amount'].sum()
        sub_df = sub_df_gb.reset_index()

    total = sub_df.groupby(['Periodo'], as_index=False)['Real_amount'].sum()
    total = total.iloc[0]['Real_amount']

    x, y = 0., 0.
    width, height = 200., 100.

    normed = sq.normalize_sizes(sub_df['Real_amount'], width, height)
    rects = sq.squarify(normed, x, y, width, height)

    color_brewer = ['rgb(166,206,227)', 'rgb(31,120,180)', 'rgb(178,223,138)',
                    'rgb(51,160,44)', 'rgb(251,154,153)', 'rgb(227,26,28)', 'rgb(137,45,89)']

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

        # print(sub_df.iloc[counter]['NIVEL3'])

        annotations.append(dict(
            x=r['x']+(r['dx']/2),
            y=r['y']+(r['dy']/2),
            text=sub_df.iloc[df_counter]['NIVEL3'].replace(' ', '<br>'),
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
        text=[str(row['NIVEL3']) + '<br>' + str(round(row['Real_amount'] / total * 100, 2)) + '%' for (i, row) in sub_df.iterrows()],
        customdata=[],
        hoverinfo='text',
        textfont=dict(size=2),
        mode='text',
    )

    layout = dict(
        height=700,
        width=1000,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        shapes=shapes,
        annotations=annotations,
        hovermode='closest'
    )

    return go.Figure(data=[trace], layout=layout)


@app.callback(
    Output('pie-charts', 'figure'),
    [Input('year-slider', 'value')]
)
def updatePieCharts(year):
    pib = df_pib[(df_pib['Periodo'] == year)].iloc[0]['PIB']
    perc_inc = df_inc[(df_inc['Periodo'] == year)].iloc[0]['Real_amount'] * 100 / pib
    perc_exp = df_exp[(df_exp['Periodo'] == year)].iloc[0]['Real_amount'] * 100 / pib

    perc_pib_inc = 100 - perc_inc
    perc_pib_exp = 100 - perc_exp

    traces = []

    traces.append(go.Pie(
        labels=['PIB', 'Ingresos'],
        values=[perc_pib_inc, perc_inc],
        hoverinfo='label+percent',
        textinfo='label',
        domain={'x': [0, 0.48]},
        name='Ingresos',
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
