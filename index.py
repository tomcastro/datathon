import os
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from apps import graph1, app2, app3, app4

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div(
        className='navbar navbar-default',
        children=html.Div(
            className='container-fluid',
            children=[
                html.Div(
                    className='navbar-header',
                    children=html.A('UAI Datathon', className='navbar-brand', href='/')
                ),
                html.Ul(
                    className='nav navbar-nav',
                    children=[
                        html.Li(className='active', children=html.A('Cruce 1', href='/graph1')),
                        html.Li(children=html.A('Cruce 2', href='/app2')),
                        html.Li(children=html.A('Cruce 3', href='/app3')),
                        html.Li(children=html.A('Cruce 4', href='/app4')),
                    ]
                )
            ]
        )
    ),

    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/graph1':
        return graph1.layout
    elif pathname == '/app2':
        return app2.layout
    elif pathname == '/app3':
        return app3.layout
    elif pathname == '/app4':
        return app4.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
