# -*- coding: utf-8 -*-

import os
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# Get CSV files depending on environment

current_path = os.getcwd()
month_path = os.path.join(current_path, 'datasets', 'dataset_1.csv')
pop_path = os.path.join(current_path, 'datasets', 'dataset_4.csv')
pib_path = os.path.join(current_path, 'datasets', 'dataset_5.csv')
imm_path = os.path.join(current_path, 'datasets',
                        'immigration_data', 'visas.csv')

# Get dataset 5

df_pib = pd.read_csv(pib_path, sep=';')
cols = df_pib.columns.values
cols[0] = 'Periodo'
cols[1] = 'PIB'
df_pib.columns = cols
df_pib = df_pib[((df_pib['Periodo']) >= 2005) & ((df_pib['Periodo']) <= 2016)]
df_pib = df_pib.reset_index(drop=True)

# Get dataset 4

df_pop = pd.read_csv(pop_path, sep=';')
df_pop = df_pop[((df_pop['Ano']) >= 2005) & ((df_pop['Ano']) <= 2016)]
df_pop = df_pop.reset_index(drop=True)

# Get immigration dataset

df_imm = pd.read_csv(imm_path, sep=',')
df_gb = df_imm.groupby(['year']).size()
df_imm = df_gb.reset_index(name='counts')


def normalize(values, bounds):
    return [bounds['desired']['lower'] +
            (x - bounds['actual']['lower']) *
            (bounds['desired']['upper'] - bounds['desired']['lower']) /
            (bounds['actual']['upper'] - bounds['actual']['lower'])
            for x in values]

# Build bubble chart

size = []

for i, row in df_pib.iterrows():
    size.append(row['PIB'] / df_pop.iloc[i]['poblaciontotal'])

l, u = 0.3, 1
scaled_size = normalize(
    size,
    {'actual': {'lower': min(size), 'upper': max(size)},
     'desired': {'lower': l, 'upper': u}}
)
scaled_size = [round(x*150) for x in scaled_size]

colors = [row['counts'] for i, row in df_imm.iterrows()]
l, u = 100, 255
scaled_colors = normalize(
    colors,
    {'actual': {'lower': min(colors), 'upper': max(colors)},
     'desired': {'lower': l, 'upper': u}}
)
scaled_colors = [round(x) for x in scaled_colors]

traces = []

minim = df_imm.loc[df_imm['counts'].idxmin()]['counts']
maxim = df_imm.loc[df_imm['counts'].idxmax()]['counts']
minim = int(round(minim / 1000) * 1000)
maxim = int(round(maxim / 1000) * 1000)
mp = int(round((minim + maxim) / 2))

traces.append(go.Scatter(
    x=df_pib['PIB'],
    y=df_pop['poblaciontotal'],
    name=df_pib['Periodo'],
    text=['{}'.format(row['Periodo']) for i, row in df_pib.iterrows()],
    mode='markers',
    marker=dict(
        size=scaled_size,
        color=scaled_colors,
        sizemode='diameter',
        showscale=True,
        colorbar=dict(
            title='Número de inmigrantes',
            titleside='top',
            tickmode='array',
            tickvals=[105, 180, 250],
            ticktext=[str(minim), str(mp), str(maxim)],
            ticks='outside'
        )
    )
))

chart_layout = go.Layout(
    xaxis=dict(title='PIB (millones de pesos)'),
    yaxis=dict(title='Población total')
)

layout = html.Div(className='container-fluid graph', children=[

    html.H2(
        children='Población vs PIB por año, y su relación con la inmigración',
        style={
            'textAlign': 'center',
        }
    ),

    html.H4(children='(más rojo -> mayor inmigración)', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='bubble-pop-by-pib',
        figure=go.Figure(data=traces, layout=chart_layout)
    )
])
