import dash
import scipy.stats as stats
import plotly.graph_objects as go
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import joblib

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv('data.txt', sep=',')
df['quarter'] = df['quarter'].str.replace("quarter", "", case=False)
df['quarter'] = pd.to_numeric(df['quarter'])

df_filtrado = df[df['actual_productivity'] < df['targeted_productivity']]

model = joblib.load('modelo_entrenado.pkl')

caracteristicas = ['smv', 'over_time', 'incentive', 'idle_time', 'idle_men', 'no_of_style_change', 'no_of_workers', 'wip']

app.layout = html.Div([
    html.Div([
        dcc.Markdown('Análisis de alternativas')
    ]),
    html.Div([
        dcc.Dropdown(
                id='yaxis-column_alternativas',
                options=[{'label': i, 'value': i} for i in caracteristicas],
                value='no_of_workers'
            ),

        #Grafica analisis de alternativas
        dcc.Graph(id='Grafica_Analisis'),
        dcc.Markdown("Incremento unidades variable seleccionada"),
        dcc.Slider(
            id='slider_alternativas',
            min=1,
            max=20,
            value=len(df['quarter'].unique()) // 2,  # Set initial value to midpoint
            marks={i: str(i) for i in range(1, 20)},
            step=None,
            tooltip={'placement': 'bottom', 'always_visible': True},
        ),


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
            dcc.Graph(id='Productividad_objetivo_vs_actual')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Productividad_objetivo_vs_actual_por_equipo')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Productividad_actual')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='Productividad_objetivo')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Markdown("Análisis univariado - Preguntas 1 a 9")]),
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in caracteristicas],
                value='no_of_workers'
            ),
        ],
        style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='Análisis_univariado')
        ], style={'width': '100%', 'display': 'inline-block'}),
    ], style={'width': '100%', 'display': 'inline-block'}),  

], style={'width': '100%', 'display': 'inline-block'})

])

@app.callback(
    Output('Grafica_Analisis', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('yaxis-column_alternativas', 'value'),
     Input('slider_alternativas', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name, valor_slider, quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])]
    dff_base = dff[dff['actual_productivity'] < dff['targeted_productivity']]
    dff_filtrado = df_filtrado[df_filtrado['quarter'].between(quarter_value[0], quarter_value[1])]
    variables_seleccionadas = ['smv', 'over_time', 'incentive', 'idle_time', 'idle_men', 'no_of_style_change', 'no_of_workers', 'wip']
    dff_alternativas = dff_filtrado[variables_seleccionadas]
    dff_alternativas[yaxis_column_name] = dff_alternativas[yaxis_column_name].apply(lambda x: x + valor_slider)

    fig = px.scatter()

    fig.add_trace(go.Scatter(x=dff_base['targeted_productivity'],
                             y=dff_base['actual_productivity'],
                             mode='markers',
                             name='Actual Productivity',
                             hovertext=dff_base['department'],
                             marker=dict(color='blue')))

    fig.add_trace(go.Scatter(x=dff_base['targeted_productivity'],
                             y=model.predict(dff_alternativas),
                             mode='markers',
                             name='Predicted Productivity',
                             hovertext=dff_base['department'],
                             marker=dict(color='green')))

    fig.add_shape(type="line", x0=dff['targeted_productivity'].min(), y0=dff['targeted_productivity'].min(),
                  x1=dff['targeted_productivity'].max(), y1=dff['targeted_productivity'].max(),
                  line=dict(color="black", width=2, dash="dash"))

    fig.update_layout(title='Grafica de análisis de alternativas',
                      title_x=0.5,
                      margin={'l': 40, 'b': 40, 't': 30, 'r': 0},
                      hovermode='closest',
                      xaxis_title='Targeted Productivity',
                      yaxis_title='Productivity',
                      legend_title='Productividad')

    return fig


@app.callback(
    Output('Análisis_univariado', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name,
                 quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter()

    fig.add_trace(px.scatter(x=dff[xaxis_column_name],
                            y=dff['actual_productivity'],
                            trendline="ols",
                            hover_name=dff['targeted_productivity']).data[0])
    
    correlation_coefficient, _ = stats.pearsonr(dff[xaxis_column_name], dff['targeted_productivity'])
    correlation_text = f'Correlación: {correlation_coefficient:.2f}'

    fig.update_layout(title=f'Grafica de análisis {xaxis_column_name} respecto a productividad actual. \n{correlation_text}',
                      title_x=0.5, margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')


    return fig

@app.callback(
    Output('Productividad_objetivo_vs_actual', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name, quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter(dff, x='targeted_productivity', y='actual_productivity', color='department', 
                     hover_name='department', title='Grafica de productividad actual vs objetivo por departamento',
                     labels={'targeted_productivity': 'Productividad Objetivo', 'actual_productivity': 'Productividad Actual'})

    fig.add_shape(type="line", x0=dff['targeted_productivity'].min(), y0=dff['targeted_productivity'].min(), 
                  x1=dff['targeted_productivity'].max(), y1=dff['targeted_productivity'].max(), 
                  line=dict(color="black", width=2, dash="dash"))

    fig.update_layout(title_x=0.5, margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, hovermode='closest')

    return fig

@app.callback(
    Output('Productividad_objetivo_vs_actual_por_equipo', 'figure'),
    [Input('xaxis-column', 'value'),
     Input('Cuarto - Quarter', 'value')])
def update_graph(xaxis_column_name, quarter_value):
    dff = df[df['quarter'].between(quarter_value[0], quarter_value[1])] 

    fig = px.scatter(dff, x='targeted_productivity', y='actual_productivity', color='team', 
                     hover_name='team', title='Grafica de productividad actual vs objetivo por equipo',
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

