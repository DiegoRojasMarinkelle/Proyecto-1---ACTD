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
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in caracteristicas if i in ['actual_productivity', 'targeted_productivity', 'over_time']],
                value='actual_productivity'
            ),
        ], 
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

        dcc.Checklist(
            id='series-checklist',
            options=[
                {'label': 'Actual Productivity', 'value': 'actual_productivity_serie'},
                {'label': 'Targeted Productivity', 'value': 'targeted_productivity_serie'}
            ],
            value=['actual_productivity_serie', 'targeted_productivity_serie']
        ),
        
        dcc.Graph(id='Grafica_Analisis'),
        dcc.RangeSlider(
            id='Cuarto - Quarter',
            min=1,
            max=len(df['quarter'].unique()),
            value=[1, len(df['quarter'].unique())],
            marks={i: str(i) for i in range(1, len(df['quarter'].unique()) + 1)},
            step=None,
            tooltip={'placement': 'bottom', 'always_visible': True},
        )

    ], style={'width': '50%', 'display': 'inline-block'}),

html.Div([
    # Parte superior derecha: Gráficos de análisis univariado
    html.Div([
        html.Div([
            dcc.Graph(id='Analisis univariado 1')
        ], style={'width': '10%', 'height': '150px', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Analisis univariado 2')
        ], style={'width': '10%', 'height': '150px', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Analisis univariado 3')
        ], style={'width': '10%', 'height': '150px', 'display': 'inline-block'}),
    ], style={'width': '100%', 'margin-top': '0px'}),

    # Parte inferior derecha: Otro gráfico
    html.Div([
        dcc.Graph(id='Grafico de torta')
    ], style={'width': '100%', 'display': 'inline-block', 'margin-top': '20px'})
], style={'width': '50%', 'float': 'right', 'display': 'inline-block'})

])


@app.callback(
    Output('Grafica_Analisis', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('Cuarto - Quarter', 'value'),
     Input('series-checklist', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 quarter_value, selected_series):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter()

    if 'actual_productivity_serie' in selected_series:
        fig.add_trace(px.scatter(x=dff[xaxis_column_name],
                                 y=dff['actual_productivity'],
                                 hover_name=dff['department']).data[0])

    if 'targeted_productivity_serie' in selected_series:
        fig.add_trace(px.scatter(x=dff[xaxis_column_name],
                                  y=dff['targeted_productivity'],
                                  hover_name=dff['department'], color_discrete_sequence=['orange']).data[0])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

