"""
    Ok. Som ni ser nedan så har jag tagit myyycket från senaste Dashgenomgången som utgångspunkt. Basically ctrl+c ctrl+v.
    Försöker testa få in lite plots och union jack som sidbakgrund på något vis.
    
    Vad vill vi annars att sidan ska kunna visa? Alltså jag antar typ alla grafer, men på vilket sätt?
    Jag tycker personligen att det känns konstigt att ersätta px inbyggda valbarhetsfunktionalitet
    med menyer i Dash. Men helt klart behöver vi kunna välja mellan grejer, eller vill vi ha allt sammanställt på
    "startsidan", liksom side-by-side? Ska vi ha någon förklarande text? //ISAK
"""


from dash import Dash, dcc, html, Input, Output, callback, dash_table, dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import load_figure_template
from dash.dependencies import Input, Output, validate_callback, State
import plotly.graph_objects as go
import plotly.io as pio

from plot_data import prepare_data_and_plots, seasonal_graph, age_data

# Försöker ändra utseendet på alla px grafer
dark_theme_layout = {
    "plot_bgcolor": "#343a40",
    "paper_bgcolor": "#343a40",
    "font": {"color": "#ffffff"},
    "title": {"x": 0.5, "xanchor":"center"},
    # Finns fler saker att ändra om vi vill
}
pio.templates["darkly"] = go.layout.Template(layout=dark_theme_layout)
pio.templates.default = "darkly"

df_UK = pd.read_csv("../src/athlete_events.csv").query("NOC == 'GBR'")

gb_rowing = df_UK[df_UK['Sport'] == 'Rowing']
gb_cycling = df_UK[df_UK['Sport'] == 'Cycling']
gb_sailing = df_UK[df_UK['Sport'] == 'Sailing']
gb_athletics = df_UK[df_UK['Sport'] == 'Athletics']

medal_trend_rowing = gb_rowing.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
medal_trend_cycling = gb_cycling.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
medal_trend_sailing = gb_sailing.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
medal_trend_athletics = gb_athletics.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
medals_per_year = df_UK.dropna(subset=['Medal']).groupby('Year').size().reset_index(name='Count')

medal_summary = []
sports = ['Cycling', 'Rowing', 'Sailing', 'Athletics']

for sport in sports:
    sport_data = df_UK[df_UK['Sport'] == sport]

    for gender in ['M', 'F']:
        medals = sport_data[sport_data['Sex'] == gender]['Medal'].value_counts()

        s_dict = {
            'Sport': sport,
            'Gender': 'Men' if gender == 'M' else 'Women',
            'Gold': medals.get('Gold', 0),
            'Silver': medals.get('Silver', 0),
            'Bronze': medals.get('Bronze', 0),
            'Total': medals.sum() 
        }
        medal_summary.append(s_dict)


athlete_names = df_UK['Name'].unique()


df_medals = df_UK.dropna(subset=['Medal'])

df_medal_counts = df_medals.pivot_table(index='NOC', columns='Medal', aggfunc='size', fill_value=0)

df_medal_counts.columns = ['Bronze', 'Silver', 'Gold']

df_medal_counts.reset_index(inplace=True)
        
medal_summary = pd.DataFrame(medal_summary)

medal_trend_df = pd.DataFrame({'Rowing': medal_trend_rowing,
                            'Cycling': medal_trend_cycling,
                            'Football': medal_trend_sailing,
                            'Athletics': medal_trend_athletics}).fillna(0)

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


app.layout = html.Div([
    dcc.Dropdown(
        id='athlete-search-dropdown',
        options=[{'label': name, 'value': name} for name in athlete_names],
        placeholder="Search for an athlete",
        style={'width': '300px', 'position': 'absolute', 'top': '10px', 'right': '10px'},
        searchable=True,
        clearable=True,
    ),
 #   profile_modal, # fick ett error här så kommenterar bort atm.
])
# Skapa en bakgrund med brittiska flaggan

app.layout = dbc.Container([
    # Background image
    html.Div([
        html.Img(src='/assets/UK-flag.png', style={
            "position": "absolute",
            "left": "0",
            "opacity": "0.4",
            "width": "100%",
            "height": "120%",
            "background-repeat": "repeat",
        }),
    ]),

    # Header row
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src='/assets/UK-flag.png',
                    style={
                        "width": "100%",
                        "opacity" : "1",
                    }
                )
            ],),
        ], width=3),
        dbc.Col(width=3),
        dbc.Col([
            html.H1("Great Britain - Olympic Games", 
                className="text-center text-primary mt-4", 
                style={"font-size": "3rem", "font-weight": "bold", "color": "#FEFEFE", "opacity": "1"}
            ),
        ], width=6),
        dbc.Col([
            html.Div([
                html.Img(src='/assets/os_flagga.jpg', style={"width": "100%"}),
            ]),
        ], width=3),
    ]),

    # Row for the athletes table
    dbc.Row([
        dbc.Col([
            gb_athletes_table
        ], width=12)
    ]),

        dcc.Dropdown(
    id='country-dropdown',
    options=[{'label': row['NOC'], 'value': row['NOC']} for index, row in df_medal_counts.iterrows()],
    value='GBR' 
    ),

    html.Div(id='country-medal-profile'),
    
    # Dropdown and Graphs
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="single_dropdown", 
                multi=True, 
                searchable=False, 
                className="mb-1",
                options=[{'label': sport, 'value': sport} for sport in medal_trend_df],
                style={"color": "#333"}
            ),
            dcc.Graph(id="medal_graph", figure={}),
            dcc.Graph(id="host_graph", figure={}),
            dcc.Graph(id="gsb_graph", figure={}),
            dcc.Graph(id="seasonal-plot", figure={}),
            dcc.Graph(id="age-data", figure={}),
            dcc.Graph(id='age-distribution-plot', figure={},
            )
        ], width=12),
    ]),
    
    # dbc.Row([
    #     dbc.Col([
    #         dash_table.DataTable(
    #             #stocks.to_dict("records"), 
    #             #id="stock_table", 
    #             #columns=[{"name": i, "id": i} for i in stocks.columns], 
    #             page_size=10, 
    #             style_cell={"textAlign": "left", "backgroundColor": "#333", "color": "#fff"}, 
    #             style_header={"backgroundColor": "#333", "color": "#fff"}, 
    #             style_data={"backgroundColor": "#333", "color": "#fff"}
#                 ),
#         ], width=6)
#     ]),
    ])

medal_trend_fig = px.line(medal_trend_df, 
    x=medal_trend_df.index,
    y=medal_trend_df.columns,
    title=f"Medal trend for {', '.join(medal_trend_df.columns)}",
    labels={'index': 'Year',
            'value': 'Medals',
            'variable': 'Sport'},
    color_discrete_sequence=['navy',
                            'red',
                            'green',
                            'orange'],
)
medal_trend_fig.update_layout(
    xaxis = dict(
        tickmode='linear',
        tick0=1896,
        dtick=4,
    )
)


host_years = [1908, 1948, 2012]

host_year_fig = px.line(medals_per_year,
            x='Year',
            y='Count',
            title='Great Britain Olympic Medals by Year and Hosted Years',
            labels={'Year': 'Year',
                    'Count': 'Medals'},
            hover_name='Year',
            hover_data={'Year': False},
            )

host_year_fig.update_layout(xaxis=dict(tickangle=70,
                            tickmode='array',
                            tickvals=medals_per_year['Year'].unique(),
                            ticktext=medals_per_year['Year'].unique())
                )
for year in host_years:
    host_year_fig.add_vline(x=year,
                            line_dash="dash",
                            line_color="red",
                            opacity=0.3,
                            annotation_text=f"UK hosted year {year}",)

gold_silver_bronze_fig = px.histogram(medal_summary, 
    x='Sport',
    y=['Gold', 'Silver', 'Bronze'],
    title=f"Medal summary for {', '.join(medal_summary['Sport'].unique())}",
    labels={'index': 'Year', 'value': 'Medals', 'variable': 'Sport'},
    barmode='group',
    color_discrete_sequence=['gold', 'silver', 'brown'],
    hover_data=['value', 'variable'],
    hover_name='variable'
    )

#Behövs ej?
#fig_all = prepare_data_and_plots()

#app.layout = html.Div([
#     html.H1("UK Athletes Age Distribution Across Different Eras"),
#     dcc.Graph(
#         id='age-distribution-plot',
#         figure=fig_all
#     )
# ])


@callback(
    Output("medal_graph", "figure"),
    Input("single_dropdown", "value")
)

#Drop down menu for different sports
def medal_graph(sport):
    if not sport:
        filtrted_df = medal_trend_df
    else:
        filtrted_df = medal_trend_df[sport]

    fig = px.line(filtrted_df,
                  x=filtrted_df.index,
                  y=filtrted_df.columns,
                  title=f"Medal trend for {', '.join(filtrted_df.columns)}",
                  labels={'index': 'year', 'value': 'medals', 'variable': 'sport'},
                  color_discrete_sequence=['navy', 'red', 'green', 'orange'])
    
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=1896,
            dtick=4,
        )
    )

    return fig


@callback(
    Output('country-medal-profile', 'children'),
    [Input('country-dropdown', 'value')]
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
    Output("host_graph", "figure"),
    Input("single_dropdown", "value")
)
def host_graph(sport):
    return host_year_fig

@callback(
    Output("gsb_graph", "figure"),
    Input("single_dropdown", "value")
)
def gsb_graph(sport):
    return gold_silver_bronze_fig

@app.callback(
    Output('age-distribution-plot', 'figure'),
    Input("single_dropdown", "value")
)
def update_graph(input_value):
    fig_all = prepare_data_and_plots()
    return fig_all

@app.callback(
    Output("seasonal-plot", "figure"),
    Input("single_dropdown", "value")
)
def seasonal(seasonal):
    fig_all = seasonal_graph()
    return fig_all

@app.callback(
    Output("age-data", "figure"),
    Input("single_dropdown", "value")
)
def age_graph(vadsom):
    fig = age_data()
    return fig

# @callback(
#     Output("closing_graph", "figure"),
#     Input("multi_dropdown", "value")
# )
# def update_closing_graph(symbols):
#     if symbols is None: symbols = []
#     df = stocks[stocks["Symbols"].isin(symbols)]
#     return px.line(df, x=df.index, y="Close", color="Symbols")


if __name__ == '__main__':
    app.run_server(debug=True)