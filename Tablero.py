

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv('data.txt', sep=',')
df['quarter'] = df['quarter'].str.replace("quarter", "", case=False)
df['quarter'] = pd.to_numeric(df['quarter'])

# Asume que df es tu DataFrame y está definido previamente
# df = pd.read_csv('tu_archivo.csv')

app.layout = html.Div([
    # Otras partes del layout van aquí
    
    # Parte superior derecha modificada para incluir 9 gráficas
    html.Div([
        html.Div([dcc.Graph(id=f'grafica_{i}') for i in range(1, 10)],
        style={'display': 'grid', 'grid-template-columns': 'repeat(3, 1fr)'})
    ], style={'width': '50%', 'float': 'right', 'display': 'inline-block'})
])

# Callbacks para actualizar cada gráfica
for i, col in enumerate(df.columns[1:], start=1):  # Asume que la primera columna no se usa para las gráficas
    @app.callback(
        Output(f'grafica_{i}', 'figure'),
        [Input('selector_de_datos', 'value')]  # Asume que tienes un Input para seleccionar datos o rangos
    )
    def update_graph(selected_value):
        # Filtra o prepara tus datos basado en 'selected_value' si es necesario
        fig = px.bar(df, x=col, y=df['actual_productivity'])  # Modifica esto según necesites
        return fig

if __name__ == '_main_':
    app.run_server(debug=True)
