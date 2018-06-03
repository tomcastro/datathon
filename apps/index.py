import dash_core_components as dcc
import dash_html_components as html

from app import app


def div(className, children=[]):
    return html.Div(className=className, children=children)


def card(title, link=''):
    return html.Div(
        className='card',
        children=[html.Div(
            className='card-body',
            children=[
                html.Div(className='img-container ' + link[1:], children=[
                    dcc.Link(href=link, children=[
                        html.Div(className='floater'),
                        html.Div(title, className='overlay')
                    ])
                ])
            ]
        )]
    )

grid = html.Div(className='grid-wrapper', children=[
    div(
        'row',
        [
            div(
                'col-sm-6',
                card('Presupuesto vs. Gasto', '/graph1')
            ),

            div(
                'col-sm-6',
                card('PIB vs. Presupuesto y Gasto', '/graph2')
            )
        ]
    ),
    div(
        'row',
        [
            div(
                'col-sm-6',
                card('PIB vs. Ingreso y Gasto', '/graph3')
            ),

            div(
                'col-sm-6',
                card('Inmigración vs. PIB y población', '/graph4')
            )
        ]
    ),
])

layout = html.Div(
    className='container-fluid graph',
    children=[
        html.H1(
            'DataScienceLab UAI - Datathon Data Campfire',
            style={'text-align': 'center'}
        ),

        html.Div(grid)
    ]
)
