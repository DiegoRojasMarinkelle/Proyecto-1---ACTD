import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv('data.txt', sep=',')
df['quarter'] = df['quarter'].str.replace("quarter", "", case=False)
df['quarter'] = pd.to_numeric(df['quarter'])

caracteristicas = df.columns

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in caracteristicas],
                value='no_of_workers'
            ),
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options = [{'label': i, 'value': i} for i in caracteristicas if i in ['actual_productivity', 'targeted_productivity', 'over_time']],
                value='actual_productivity'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic'),

    dcc.RangeSlider(
        id='Cuarto - Quarter',
        min=1,
        max=len(df['quarter'].unique()),
        value=[1, len(df['quarter'].unique())],
        marks={i: str(i) for i in range(1, len(df['quarter'].unique()) + 1)},
        step=None
    )
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('xaxis-type', 'value'),
     Input('yaxis-type', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter(x=dff[xaxis_column_name],
                     y=dff[yaxis_column_name],
                     hover_name=dff['actual_productivity'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=xaxis_column_name, 
                     type='linear' if xaxis_type == 'Linear' else 'log') 

    fig.update_yaxes(title=yaxis_column_name, 
                     type='linear' if yaxis_type == 'Linear' else 'log') 

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

