import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import index, graph1, graph2, graph3, graph4

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div(children=[html.Div(
        html.Ul(
            className='custom-nav',
                children=[
                    html.Li(className='active', children=html.A('Cruce 1', href='/graph1')),
                    html.Li(children=html.A('Cruce 2', href='/graph2')),
                    html.Li(children=html.A('Cruce 3', href='/graph3')),
                    html.Li(children=html.A('Cruce 4', href='/graph4')),
                ]
            )
        )
    ]),

    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/graph1':
        return graph1.layout
    elif pathname == '/graph2':
        return graph2.layout
    elif pathname == '/graph3':
        return graph3.layout
    elif pathname == '/graph4':
        return graph4.layout
    elif pathname == '/':
        return index.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
