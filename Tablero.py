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
        dcc.Checklist(
            id='series-checklist',
            options=[
                {'label': 'Actual Productivity', 'value': 'actual_productivity_serie'},
                {'label': 'Targeted Productivity', 'value': 'targeted_productivity_serie'}
            ],
            value=['actual_productivity_serie', 'targeted_productivity_serie']
        ),
        
        #Grafica analisis de alternativas
        dcc.Graph(id='Grafica_Analisis'),
        dcc.Markdown('Cuarto - Quarter'),
        dcc.RangeSlider(
            id='Cuarto - Quarter',
            min=1,
            max=len(df['quarter'].unique()),
            value=[1, len(df['quarter'].unique())],
            marks={i: str(i) for i in range(1, len(df['quarter'].unique()) + 1)},
            step=None,
            tooltip={'placement': 'bottom', 'always_visible': True},
        )

    ], style={'width': '100%', 'display': 'inline-block'}),

html.Div([
    #Gráficos de análisis univariado
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
        
        html.Div([
            dcc.Graph(id='Productividad_objetivo_vs_actual')
        ], style={'width': '100%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Productividad_actual')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Productividad_objetivo')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Análisis_univariado')
        ], style={'width': '100%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='no_of_style_change')
        ], style={'width': '10%', 'display': 'inline-block'}), 
        html.Div([
            dcc.Graph(id='targeted_productivity')
        ], style={'width': '10%', 'display': 'inline-block'}), 
    ], style={'width': '100%', 'display': 'inline-block'}),  

    
    # Parte inferior derecha: Otro gráfico
    html.Div([
        dcc.Graph(id='Grafico de torta1')
    ], style={'width': '100%', 'display': 'inline-block'}),
], style={'width': '100%', 'display': 'inline-block'})



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

    fig.update_layout(title='Grafica de análisis de alternativas', title_x=0.5, margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')

    return fig

@app.callback(
    Output('Análisis_univariado', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name,
                 quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter()

    fig.add_trace(px.scatter(x=dff[xaxis_column_name],
                            y=dff[yaxis_column_name],
                            trendline="ols",
                            hover_name=dff['actual_productivity']).data[0])

    fig.update_layout(title='Grafica de análisis univariado respecto a productividad actual', title_x=0.5, margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')

    return fig

@app.callback(
    Output('Productividad_objetivo_vs_actual', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name, quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter(dff, x='targeted_productivity', y='actual_productivity', color='department', 
                     hover_name='department', title='Grafica de análisis univariado respecto a productividad actual',
                     labels={'targeted_productivity': 'Productividad Objetivo', 'actual_productivity': 'Productividad Actual'})

    fig.add_shape(type="line", x0=dff['targeted_productivity'].min(), y0=dff['targeted_productivity'].min(), 
                  x1=dff['targeted_productivity'].max(), y1=dff['targeted_productivity'].max(), 
                  line=dict(color="black", width=2, dash="dash"))

    fig.update_layout(title_x=0.5, margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')

    return fig

@app.callback(
    Output('Productividad_actual', 'figure'),
    [Input('Cuarto - Quarter', 'value')])
def update_graph(quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    # Calcula el promedio de la actual_productivity por departamento
    avg_productivity = dff.groupby('department')['actual_productivity'].mean().reset_index()

    fig = px.bar(avg_productivity, x='department', y='actual_productivity',
                 hover_data={'actual_productivity': ':.2f'})

    fig.update_layout(title='Promedio de Productividad Actual por Departamento',
                      xaxis_title='Departamento', yaxis_title='Promedio de Productividad',
                      margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')

    return fig

@app.callback(
    Output('Productividad_objetivo', 'figure'),
    [Input('Cuarto - Quarter', 'value')])
def update_graph(quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    # Calcula el promedio de la targeted_productivity por departamento
    avg_productivity = dff.groupby('department')['targeted_productivity'].mean().reset_index()

    fig = px.bar(avg_productivity, x='department', y='targeted_productivity',
                 hover_data={'targeted_productivity': ':.2f'})

    fig.update_layout(title='Promedio de Productividad Actual por Departamento',
                      xaxis_title='Departamento', yaxis_title='Promedio de Productividad',
                      margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

