import dash

app = dash.Dash(__name__.split('.')[0], static_folder='assets')
server = app.server
app.config.suppress_callback_exceptions = True
# app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.css.append_css({'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css'})
app.css.append_css({'external_url': 'https://codepen.io/tomcastro/pen/yEyvmQ.css'})

# app.scripts.append_script({'external_url': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.bundle.min.js'})
