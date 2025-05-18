from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
df = df[df['country'].notna()]

available_countries = sorted(df['country'].unique())
metrics = ['lifeExp', 'gdpPercap', 'pop']
years = sorted(df['year'].unique())

app = Dash(__name__)
app.title = "Глобальная статистика"

app.layout = html.Div([
    html.H1("Глобальная статистика стран", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Страны:"),
        dcc.Dropdown(
            options=[{'label': c, 'value': c} for c in available_countries],
            value=['Japan', 'Russia'],
            multi=True,
            id='country-dropdown'
        )
    ], style={'margin': '10px'}),

    html.Div([
        html.Label("Метрика:"),
        dcc.Dropdown(
            options=[{'label': m, 'value': m} for m in metrics],
            value='lifeExp',
            id='metric-dropdown'
        )
    ], style={'margin': '10px'}),

    html.Div([
        html.Label("Год:"),
        dcc.Dropdown(
            options=[{'label': str(year), 'value': year} for year in years],
            value=2007,
            id='year-dropdown',
            clearable=False
        )
    ], style={'margin': '20px'}),

    dcc.Graph(id='line-graph'),
    dcc.Graph(id='bubble-chart'),
    dcc.Graph(id='top15-population'),
    dcc.Graph(id='continent-pie')
])

# линейный график
@app.callback(
    Output('line-graph', 'figure'),
    Input('country-dropdown', 'value'),
    Input('metric-dropdown', 'value')
)
def update_line_graph(countries, metric):
    dff = df[df['country'].isin(countries)]
    fig = px.line(dff, x='year', y=metric, color='country',
                  labels={'year': 'Год', metric: metric})
    fig.update_layout(title='Динамика метрики по странам')
    return fig

# пузырьковая диаграмма
@app.callback(
    Output('bubble-chart', 'figure'),
    Input('year-dropdown', 'value'),
    Input('metric-dropdown', 'value')
)
def update_bubble(year, metric):
    dff = df[df['year'] == year]
    fig = px.scatter(dff, x='gdpPercap', y=metric, size='pop', color='continent',
                     hover_name='country', size_max=60, log_x=True,
                     labels={'gdpPercap': 'GDP per Capita', metric: metric})
    fig.update_layout(title=f'Пузырьковая диаграмма: {year}')
    return fig

# топ-15 стран по населению
@app.callback(
    Output('top15-population', 'figure'),
    Input('year-dropdown', 'value')
)
def update_top15(year):
    dff = df[df['year'] == year].nlargest(15, 'pop')
    fig = px.bar(dff, x='country', y='pop', color='continent',
                 labels={'pop': 'Население'}, title=f'Топ-15 стран по населению ({year})')
    return fig

# круговая диаграмма по континентам
@app.callback(
    Output('continent-pie', 'figure'),
    Input('year-dropdown', 'value')
)
def update_pie(year):
    dff = df[df['year'] == year]
    pie_df = dff.groupby('continent', as_index=False)['pop'].sum()
    fig = px.pie(pie_df, names='continent', values='pop',
                 title=f'Население по континентам ({year})')
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8057)
