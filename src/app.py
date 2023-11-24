from dash import Dash, dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.io as pio

from plot_data import get_data, get_medal_counts, get_medal_trend_df, medal_trend_fig, host_year_fig, gold_silver_bronze_fig, age_distri_eras_bar, age_distri_eras_scatter, seasonal_graph, age_data

df_all_countries = get_data()[0]
df_UK = get_data()[1]

medals_per_year = df_UK.dropna(subset=['Medal']).groupby('Year').size().reset_index(name='Count')
sports = ['Cycling', 'Rowing', 'Sailing', 'Athletics']
athlete_names = df_all_countries['Name'].unique()
df_medal_counts = get_medal_counts()
medal_trend_df = get_medal_trend_df()

dark_theme_layout = {
    "plot_bgcolor": "#343a40",
    "paper_bgcolor": "#343a40",
    "font": {"color": "#ffffff"},
    "title": {"x": 0.5, "xanchor":"center"},
}
pio.templates["darkly"] = go.layout.Template(layout=dark_theme_layout)
pio.templates.default = "darkly"

app = Dash(__name__,
        external_stylesheets=[dbc.themes.DARKLY],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"},],)

server = app.server

gb_athletes_table = dash_table.DataTable(
    id='gb_athletes_table',
    columns=[{"name": i, "id": i} for i in df_UK.columns],
    data=df_UK.to_dict('records'),
    filter_action='native',
    sort_action='native',
    page_action='native',
    page_size=10,
    style_table={
        'maxWidth': '100%', 
        'overflowX': 'auto'
    },
    style_cell={
        'minWidth': '100px', 
        'maxWidth': '180px', 
        'width': '150px',
        'textAlign': 'left', 
        'backgroundColor': '#888', 
        'color': '#fff'
    },
    style_header={
        'backgroundColor': '#333', 
        'color': '#fff'
    },
    style_data={
        'backgroundColor': '#333', 
        'color': '#fff'
    }
)


app.layout = dbc.Container([
    
    # Background
        html.Div([
        html.Img(src='/assets/UK-flag.png',
                style={
                    "position": "absolute",
                    "left": "0",
                    "opacity": "0.2",
                    "width": "100%",
                    "height": "100%",
                }
            )
        ]),
        
    # Row for the title and union-jack/OS flag
    dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src='/assets/UK-flag.png',
                        style={
                            "width": "100%"
                        }
                    )
                ]),
            ], width=3),
            dbc.Col([
                html.H1("UK - Olympic Games",
                    style={"opacity": "200%",
                        "color": "#fff",
                        "text-align": "center",
                        "top": "50%",}, 
                ),
            ], width=6),
            dbc.Col([
                html.Div([
                    html.Img(src='/assets/os_flagga.jpg', style={"width": "100%"}),
                ]),
            ], width=3),
        ], style={"opacity": "1"}),

    # Row for the athletes table
    dbc.Row([
        dbc.Col([
            gb_athletes_table
        ], width=12)
    ]),
    
    # Row for the dropdowns
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='athlete-search-dropdown',
                options=[{'label': name, 'value': name} for name in athlete_names],
                placeholder="Search for an athlete",
                style={'color': '#333',
                    'text-align': 'center'},
                searchable=True,
                clearable=True,
            ),
            html.Div(id='athlete-medals',
                style={"text-align": "center"}),
    ], width={"size": 6, "order": 1}),
        dbc.Col([
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': row['NOC'], 'value': row['NOC']} for index, row in df_medal_counts.iterrows()],
                value='GBR',
                style={"color": "#333",
                    "text-align": "center"}
            ),
            html.Div(id='country-medal-profile',
                style={"text-align": "center"}),
    ], width={"size": 6, "order": 2}),
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown( # Dropdown for choosing sports in graph 1
                id="single_dropdown", 
                multi=True, 
                searchable=True, 
                className="mb-1",
                options=[{'label': sport, 'value': sport} for sport in medal_trend_df],
                style={"color": "#333"}
            ), 
                dcc.Graph(id="medal_graph", figure={}), # All our graphs
                dcc.Graph(id="host_graph", figure={}),
                dcc.Graph(id="gsb_graph", figure={}),
                dcc.Graph(id="seasonal-plot", figure={}),
                dcc.Graph(id="age-data", figure={}),
                dcc.Graph(id='age-distribution-plot', figure={},
            ),
            dcc.Dropdown( # Dropdown for the last graph
                id='time-period-dropdown',
                options=[
                    {'label': 'Pre-WW1', 'value': 'pre_ww1'},
                    {'label': 'Between Wars', 'value': 'between_wars'},
                    {'label': 'Post-WW2 Pre-1989', 'value': 'post_ww2_pre_1989'},
                    {'label': 'Post-1989', 'value': 'post_1989'}
                ],
                style={"color": "#333"},
                value=['pre_ww1', 'between_wars', 'post_ww2_pre_1989', 'post_1989'],
                multi=True
            ),
                dcc.Graph(id='age-distribution-scatter')
        ], width=12),
    ]),
])

# ---------------CALLBACKS----------------

@callback(
    Output('country-medal-profile', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_profile(selected_country):
    country_data = df_medal_counts[df_medal_counts['NOC'] == selected_country]

    if country_data.empty:
        return html.P("No data available for this country.", style={'color': 'red'})

    country_data = country_data.iloc[0]

    profile = html.Div([
        html.H3(f"Country: {selected_country}"),
        html.P(f"Gold Medals: {country_data['Gold']}"),
        html.P(f"Silver Medals: {country_data['Silver']}"),
        html.P(f"Bronze Medals: {country_data['Bronze']}")
    ])

    return profile

@callback(
    Output("medal_graph", "figure"),
    Input("single_dropdown", "value")
)

def medal_graph(sport):
    fig = medal_trend_fig(sport)
    return fig

@callback(
    Output("host_graph", "figure"),
    Input("single_dropdown", "value")
)
def host_graph(sport):
    fig = host_year_fig()
    return fig

@callback(
    Output("gsb_graph", "figure"),
    Input("single_dropdown", "value")
)
def gsb_graph(sport):
    fig = gold_silver_bronze_fig()
    return fig

@app.callback(
    Output('age-distribution-plot', 'figure'),
    Input("single_dropdown", "value")
)
def update_graph(input_value):
    fig = age_distri_eras_bar()
    return fig

@app.callback(
    Output("seasonal-plot", "figure"),
    Input("single_dropdown", "value")
)
def seasonal(seasonal):
    fig = seasonal_graph()
    return fig

@app.callback(
    Output("age-data", "figure"),
    Input("single_dropdown", "value")
)
def age_graph(vadsom):
    fig = age_data()
    return fig

@app.callback(
    Output('age-distribution-scatter', 'figure'),
    [Input('time-period-dropdown', 'value')]
)
def age_distri_eras_scat(selected_periods):
    fig = age_distri_eras_scatter(selected_periods)
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)