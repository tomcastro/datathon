# -*- coding: utf-8 -*-

import dash
import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# Get CSV files depending on environment

if 'ENV' in os.environ and os.environ['ENV'] == 'dev':
    current_path = os.getcwd()
    exp_path = os.path.join(current_path, 'datasets', 'dataset_2.csv')
    pop_path = os.path.join(current_path, 'datasets', 'dataset_4.csv')
else:
    base_url = 'http://s3.amazonaws.com/uai-datathon-datasets/datasets/'
    exp_path = base_url + 'dataset_2.csv'
    pop_path = base_url + 'dataset_4.csv'

# Get dataset 2, rename last column, group by category and year

df_gastos = pd.read_csv(exp_path, sep=';')
cols = df_gastos.columns.values
cols[-1] = 'Gastos'
df_gastos.columns = cols

df_gb = df_gastos.groupby(['Partida', 'Periodo'])['Gastos'].sum()

df_gastos = df_gb.reset_index()

CATEGORIES = df_gastos['Partida'].unique()

# dataset 4

df_pop = pd.read_csv(pop_path, sep=';')
cols = df_pop.columns.values
cols[0] = 'year'
df_pop.columns = cols

BAR_TYPES = ['poblacionhombres', 'poblacionmujeres']
BAR_NAMES = ['Población Hombres', 'Población Mujeres']

# Initialize Dash app

app = dash.Dash(__name__.split('.')[0], static_folder='assets')
server = app.server
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True
# app.css.append_css({
#     "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
# })

app.layout = html.Div(children=[
    html.Link(
        href=os.path.join('assets', 'plotly.css'),
        rel='stylesheet'
    ),

    html.H1(children='Data Campfire Datathon', style={
        'textAlign': 'center',
    }),

    dcc.Dropdown(
        id='categories',
        options=[{
            'label': i, 'value': i
        } for i in df_gastos['Partida'].unique()],
        multi=True
    ),

    dcc.Graph(
        id='expenditure-by-section'
    ),

    dcc.Graph(
        id='pop-by-year',
        figure={
            'data': [
                go.Bar(
                    x=df_pop['year'],
                    y=df_pop[cat],
                    name=name
                ) for (cat, name) in zip(BAR_TYPES, BAR_NAMES)
            ],
            'layout': go.Layout(
                barmode='stack'
            )
        }
    )
])


@app.callback(
    dash.dependencies.Output('expenditure-by-section', 'figure'),
    [dash.dependencies.Input('categories', 'value')]
)
def updateLineChart(categories):
    if categories is None or categories == []:
        categories = CATEGORIES

    sub_df = df_gastos[(df_gastos['Partida'].isin(categories))]

    traces = []

    for cat in categories:
        trace = go.Scatter(
                    x=sub_df[sub_df.Partida == cat].Periodo,
                    y=sub_df[sub_df.Partida == cat].Gastos,
                    name=cat
                )
        traces.append(trace)

    return {'data': traces}

if __name__ == '__main__':
    app.run_server(debug=True)
