import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import index, graph1, graph2, graph3, graph4

app.title = 'DataScienceLab UAI'

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div(children=[html.Div(
        html.Ul(
            className='custom-nav',
            children=[
                html.Li(className='active', children=dcc.Link('DataScienceLab', href='/')),
                html.Li(id='back', className='float-right back-button-no-display', children=[
                    dcc.Link('Volver al inicio', href='/')
                ])
            ]
        )
    )]),

    html.Div(id='page-content')
])


@app.callback(Output('back', 'className'),
              [Input('url', 'pathname')])
def showBackButton(pathname):
    if pathname == '/':
        return 'float-right back-button-no-display'
    else:
        return 'float-right back-button-display'


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
