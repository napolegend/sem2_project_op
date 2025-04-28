import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import numpy as np
from scipy import stats

# Загрузка и обработка данных
def parse_price_history(history_str):
    try:
        history = json.loads(history_str.replace("'", '"'))
        return [{'dt': datetime.utcfromtimestamp(item['dt']),
                 'price': item['price']['RUB'] / 100}
                for item in history]
    except:
        return None

df = pd.read_csv('../data/wildberries_data_all.csv',
                 converters={"История_цен": parse_price_history,
                            "Текущая_цена": lambda x: int("".join(x[:-1].split()))})


# Создание Dash приложения
app = dash.Dash(__name__)
server = app.server

# Разметка приложения
app.layout = html.Div([
    html.H1("Анализ цен Wildberries", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Выберите артикул товара:"),
        dcc.Dropdown(
            id='article-dropdown',
            options=[{'label': str(art), 'value': art}
                    for art in df['Артикул'].unique()],
            value=df['Артикул'].iloc[0]
        )
    ], style={'width': '50%', 'margin': '20px'}),

    dcc.Graph(id='price-history-plot'),

    html.Div([
        html.Div([
            dcc.Graph(id='price-distribution')
        ], style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            html.H3("Статистика цен"),
            html.Div(id='price-stats-table')
        ], style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ])
])

# Callback для обновления графиков
@app.callback(
    [Output('price-history-plot', 'figure'),
     Output('price-distribution', 'figure'),
     Output('price-stats-table', 'children')],
    [Input('article-dropdown', 'value')]
)
def update_plots(selected_article):
    # Выбор нужных данных
    filtered_df = df[df['Артикул'] == selected_article]
    price_history = filtered_df['История_цен'].iloc[0]

    # График истории цен
    history_fig = px.line(
        pd.DataFrame(price_history),
        x='dt',
        y='price',
        title=f"Динамика цены для артикула {selected_article}",
        labels={'dt': 'Дата', 'price': 'Цена (руб)'}
    )

    # Гистограмма распределения всех цен
    dist_fig = px.histogram(
        df,
        x='Текущая_цена',
        nbins=30,
        title='Распределение текущих цен',
        labels={'Текущая_цена': 'Цена (руб)'}
    )

    # Общая стата по датасету
    stats_df = df['Текущая_цена'].describe().reset_index()
    stats_table = dash.dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in stats_df.columns],
        data=stats_df.to_dict('records'),
        style_cell={'padding': '5px'}
    )

    return history_fig, dist_fig, stats_table

if __name__ == '__main__':
    app.run(debug=False)
