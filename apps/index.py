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

        html.Div(className='text-container', children=[
            html.P(
                'El PIB percapita ha crecido anualmente a la misma tasa del crecimiento en población e inmigrantes, teniendo un efecto positivo. Sin embargo el presupuesto y gasto del aparato público excede en varios órdenes de magnitud el de otros ministerios importantes como Salud y Educación.',
                className='intro-paragraph'
            )
        ]),

        html.Div(grid),

        html.Div(className='text-container', children=[
            html.Ul(className='list', children=[
                html.Li('La administración pública requiere eficiencia operacional para lograr liberar fondos que sirvan para apoyar las políticas públicas en Salud, Educación y Seguridad'),
                html.Li('El patrón de ejecución de gasto mensual de cada institución se mantiene durante los últimos años. Aquí podría haber una mejora en agilizar la asignación de los presupuestos y acelerar su entrega para que los proyectos no sufran retrasos y los ciudadanos no se vean afectados por la demora en la ejecución de las politicas públicas del gobierno de turno.'),
                html.Li('El crecimiento del PIB anual no se ve afectado por el crecimiento en el presupuesto y gasto anual. Las gestión económica ha sido cuidadosa de mantener en orden los ingresos y egresos del país.')
            ])
        ])
    ]
)
