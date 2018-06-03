import dash_core_components as dcc
import dash_html_components as html

from app import app


def div(className, children=[]):
    return html.Div(className=className, children=children)


def card(title, img=''):
    return html.Div(
        className='card',
        children=[html.Div(
            className='card-body',
            children=[
                html.Div(className='img-container', children=[
                    html.Div(title, className='overlay')
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
                card('Gráfico 1', 'https://i.imgur.com/mZK8ya6.jpg')
            ),

            div(
                'col-sm-6',
                card('Gráfico 2', 'https://i.imgur.com/mZK8ya6.jpg')
            )
        ]
    ),
    div(
        'row',
        [
            div(
                'col-sm-6',
                card('Gráfico 3', 'https://i.imgur.com/mZK8ya6.jpg')
            ),

            div(
                'col-sm-6',
                card('Gráfico 4', 'https://i.imgur.com/mZK8ya6.jpg')
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
