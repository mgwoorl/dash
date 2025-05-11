from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# загрузка данных
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
available_countries = df['country'].unique()
available_metrics = ['lifeExp', 'gdpPercap', 'pop']
available_years = sorted(df['year'].unique())

# инициализация приложения
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Задание по Dash"),

    html.Div([
        html.Label("Выберите страны:"),
        dcc.Dropdown(
            options=[{'label': c, 'value': c} for c in available_countries],
            value=['Canada', 'South Korea'],
            multi=True,
            id='country-dropdown'
        ),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Label("Выберите метрику (ось Y):"),
        dcc.Dropdown(
            options=[{'label': m, 'value': m} for m in available_metrics],
            value='lifeExp',
            id='metric-dropdown'
        )
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Label("Выберите год:"),
        dcc.Slider(
            min=min(available_years),
            max=max(available_years),
            step=5,
            value=2007,
            marks={str(year): str(year) for year in available_years},
            id='year-slider'
        )
    ], style={'marginBottom': '40px'}),

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
def update_line_graph(selected_countries, selected_metric):
    dff = df[df['country'].isin(selected_countries)]
    fig = px.line(dff, x='year', y=selected_metric, color='country',
                  labels={selected_metric: selected_metric, 'year': 'Year'})
    fig.update_layout(title='Метрика по странам во времени')
    return fig

# пузырьковая диаграмма
@app.callback(
    Output('bubble-chart', 'figure'),
    Input('year-slider', 'value'),
    Input('metric-dropdown', 'value')
)
def update_bubble_chart(selected_year, selected_metric):
    dff = df[df['year'] == selected_year]
    fig = px.scatter(
        dff,
        x='gdpPercap',
        y=selected_metric,
        size='pop',
        color='continent',
        hover_name='country',
        log_x=True,
        size_max=60,
        labels={'gdpPercap': 'GDP per Capita', selected_metric: selected_metric}
    )
    fig.update_layout(title=f'Пузырьковая диаграмма ({selected_year})')
    return fig

# топ-15 стран по населению
@app.callback(
    Output('top15-population', 'figure'),
    Input('year-slider', 'value')
)
def update_top15_pop(selected_year):
    dff = df[df['year'] == selected_year].nlargest(15, 'pop')
    fig = px.bar(
        dff,
        x='country',
        y='pop',
        color='continent',
        title=f'Топ-15 стран по населению ({selected_year})',
        labels={'pop': 'Population'}
    )
    return fig

# круговая диаграмма по континентам
@app.callback(
    Output('continent-pie', 'figure'),
    Input('year-slider', 'value')
)
def update_pie_chart(selected_year):
    dff = df[df['year'] == selected_year]
    continent_sum = dff.groupby('continent')['pop'].sum().reset_index()
    fig = px.pie(
        continent_sum,
        values='pop',
        names='continent',
        title=f'Распределение населения по континентам ({selected_year})'
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)