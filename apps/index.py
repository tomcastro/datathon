import dash_core_components as dcc
import dash_html_components as html

from app import app


def div(className, children=[]):
    return html.Div(className=className, children=children)


def card(title):
    return html.Div(
        className='card',
        children=[html.Div(
            className='card-body',
            children=[
                html.H5(title, className='card-title')
            ]
        )]
    )

grid = [
    div(
        'row',
        [
            div(
                'col-sm-6',
                card('Gráfico 1')
            ),

            div(
                'col-sm-6',
                card('Gráfico 2')
            )
        ]
    ),
    div(
        'row',
        [
            div(
                'col-sm-6',
                card('Gráfico 3')
            ),

            div(
                'col-sm-6',
                card('Gráfico 4')
            )
        ]
    ),
]

layout = html.Div(
    className='container graph',
    children=[
        html.H1(
            'DataScienceLab UAI - Datathon Data Campfire',
            style={'text-align': 'center'}
        ),

        html.Div(grid)
    ]
)
