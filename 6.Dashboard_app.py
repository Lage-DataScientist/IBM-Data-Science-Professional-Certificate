import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

spacex_df= pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
spacex_df.head()

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

app = dash.Dash(__name__)

# Get unique launch sites
launch_sites = spacex_df['Launch Site'].unique().tolist()
# Lista de sites únicos
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Define o layout do aplicativo
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # Dropdown para selecionar o site de lançamento
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
    ),

    html.Br(),

    # Gráfico de pizza para mostrar a taxa de sucesso
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):", style={'font-size': '20px'}),

    # Slider para selecionar o intervalo de massa do payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}' for i in range(0, 10001, 1000)}, # Marcas a cada 1000 kg
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # Gráfico de dispersão para mostrar a relação entre payload, classe e booster
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback para atualizar o gráfico de pizza (Success Pie Chart)
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Se 'ALL' for selecionado, calcula a contagem de sucesso (class=1) para todos os sites
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches By Site')
        return fig
    else:
        # Se um site específico for selecionado, filtra os dados para esse site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Conta a ocorrência de sucesso (class=1) e falha (class=0) para o site selecionado
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        
        # Mapeia 0 para 'Failure' e 1 para 'Success' para melhor visualização
        success_counts['class'] = success_counts['class'].map({0: 'Failure', 1: 'Success'})

        fig = px.pie(success_counts, values='count',
                     names='class',
                     title=f'Total Success and Failure Launches for site {entered_site}')
        return fig

# Callback para atualizar o gráfico de dispersão (Success Payload Scatter Chart)
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    # Filtra os dados com base no intervalo de payload selecionado
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if entered_site == 'ALL':
        # Se 'ALL' for selecionado, mostra todos os pontos de dados no intervalo de payload
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        # Se um site específico for selecionado, filtra ainda mais por esse site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for site {entered_site}')
        return fig

# Executa o aplicativo
if __name__ == '__main__':
    app.run(debug=True)