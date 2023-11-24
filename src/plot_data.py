import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

# Data import

def get_data():
    athlete_events = pd.read_csv("athlete_events.csv")
    UK_athletes = athlete_events[athlete_events['NOC'] == 'GBR']
    return athlete_events, UK_athletes

# Variables structure

athlete_events = get_data()[0]
UK_athletes = athlete_events[athlete_events['NOC'] == 'GBR']

gb_rowing = UK_athletes[UK_athletes['Sport'] == 'Rowing']
gb_cycling = UK_athletes[UK_athletes['Sport'] == 'Cycling']
gb_sailing = UK_athletes[UK_athletes['Sport'] == 'Sailing']
gb_athletics = UK_athletes[UK_athletes['Sport'] == 'Athletics']

athlete_names = athlete_events['Name'].unique()

medals_per_year = UK_athletes.dropna(subset=['Medal']).groupby('Year').size().reset_index(name='Count')

medal_summary = []
sports = ['Cycling', 'Rowing', 'Sailing', 'Athletics']

for sport in sports:
    sport_data = UK_athletes[UK_athletes['Sport'] == sport]

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
medal_summary = pd.DataFrame(medal_summary)

# Func variables

def get_medal_trend_df(): # Very wierd, tried to "one-line" it, but the functionality in the choose sport dropdown dissapeared (AttributeError: 'Series' object has no attribute 'columns')
    medal_trend_rowing = gb_rowing.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
    medal_trend_cycling = gb_cycling.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
    medal_trend_sailing = gb_sailing.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
    medal_trend_athletics = gb_athletics.dropna(subset=['Medal']).groupby('Year')['Medal'].count()
    
    medal_trend_df = pd.DataFrame({'Rowing': medal_trend_rowing,
                            'Cycling': medal_trend_cycling,
                            'Sailing': medal_trend_sailing,
                            'Athletics': medal_trend_athletics}).fillna(0)
    return medal_trend_df

def get_medal_counts():
    df_medal_counts = athlete_events.dropna(subset=['Medal']).pivot_table(index='NOC', columns='Medal', aggfunc='size', fill_value=0)
    df_medal_counts.columns = ['Bronze', 'Silver', 'Gold']
    df_medal_counts.reset_index(inplace=True)
    return df_medal_counts

# Medal trend fig

def medal_trend_fig(sport):
    if not sport:
        filtered_df = get_medal_trend_df()
    else:
        filtered_df = get_medal_trend_df()[sport]
        
    medal_trend_fig = px.line(filtered_df, 
        x=filtered_df.index,
        y=filtered_df.columns,
        title=f"Medal trend for {', '.join(filtered_df.columns)}",
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
            tickangle=70,
            tickmode='linear',
            tick0=1896,
            dtick=4,
        )
    )
    
    return medal_trend_fig

# Host years fig

def host_year_fig():
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
                                opacity=0.7,
                                annotation_text=f"UK hosted year {year}",)
    return host_year_fig

# Gold, Silver, Bronze fig

def gold_silver_bronze_fig():
    gold_silver_bronze_fig = px.histogram(medal_summary, 
        x='Sport',
        y=['Gold', 'Silver', 'Bronze'],
        title=f"Medal summary for {', '.join(medal_summary['Sport'].unique())}",
        labels={'index': 'Year',
                'value': 'Medals',
                'variable': 'Sport'},
        barmode='group',
        color_discrete_sequence=['gold', 'silver', '#CD7F32'],
        hover_data=['value', 'variable'],
        hover_name='variable'
    )
    return gold_silver_bronze_fig


# UK seasonal graph

def seasonal_graph():
    UK_seasonal = UK_athletes[UK_athletes['Medal'].notna()].groupby(['Year', 'Season'])['Medal'].count().reset_index()
    UK_seasonal.rename(columns={'Medal': 'Total Medals'}, inplace=True)
    fig = px.bar(UK_seasonal,
                x='Year', y='Total Medals', color='Season',
                title='Total Olympic Medals Won by Great Britain by Year and Season',
                labels={'Year': 'Olympic Year', 'Total Medals': 'Total medals won'},
                )

    fig.update_layout(hovermode="x unified",
                    barmode='group', 
                    xaxis_tickangle=70,
                    )
    return fig

# Get age data

def age_data():
    df_age = UK_athletes[['Age', 'Name']].groupby(['Name', 'Age']).count().reset_index()
    fig = px.histogram(df_age, x='Age', title="Age distribution UK's Data")
    fig.update_layout(hovermode="x unified")
    return fig

# Plots for Age Distribution of UK Athletes before, between and after the World Wars

def age_distri_eras_bar():
    get_eras()
    
    fig_all = make_subplots()
    
    fig_all.add_trace(go.Histogram(x=get_eras()[0]['Age'], nbinsx=50, name="< 1914, Age Distribution of UK's Athletes"))
    fig_all.add_trace(go.Histogram(x=get_eras()[1]['Age'], nbinsx=50, name="1914-1940, Age Distribution of UK's Athletes between WWI & WWII" ))
    fig_all.add_trace(go.Histogram(x=get_eras()[2]['Age'], nbinsx=50, name="1945 - 1989, Age Distribution of UK's Athletes After WWII"))
    fig_all.add_trace(go.Histogram(x=get_eras()[3]['Age'], nbinsx=50, name="1989 Onwards, Age Distribution of UK's Athletes"))

    fig_all.update_layout(title_text="Age Distribution of UK's Athletes Across Different Eras",
                        xaxis_title_text="Age",
                        yaxis_title_text="Number of Athletes",
                        bargap=0.02,
                        bargroupgap=0.01,
                        hovermode="x unified",
                        legend=dict(
                                yanchor="top",
                                y=0.99,
                                xanchor="right",
                                x=0.99))

    return fig_all

def age_distri_eras_scatter(selected_periods):
    if not isinstance(selected_periods, list):
        selected_periods = [selected_periods]

    frames = {
        'pre_ww1': get_eras()[0].copy().assign(Period="< 1914, Age Distribution of UK's Athletes"),
        'between_wars': get_eras()[1].copy().assign(Period="1914-1940, Age Distribution of UK's Athletes between WWI & WWII"),
        'post_ww2_pre_1989': get_eras()[2].copy().assign(Period="1945 - 1989, Age Distribution of UK's Athletes After WWII"),
        'post_1989': get_eras()[3].copy().assign(Period="1989 Onwards, Age Distribution of UK's Athletes")
    }

    df_combined = pd.concat([frames[period] for period in selected_periods if period in frames])
    df_age_counts = df_combined.groupby(['Age', 'Period']).size().reset_index(name='Count')

    fig = px.scatter(df_age_counts,
                    x='Age',
                    y='Count',
                    color='Period',
                    title='Age Distribution of UK Athletes Over Historical Periods')

    fig.update_layout(
        xaxis_title='Age',
        yaxis_title='Number of Athletes',
        legend_title='Historical Period',
        legend=dict(
                                yanchor="top",
                                y=0.99,
                                xanchor="right",
                                x=0.99)
    )

    return fig

# Helper for above funcs

def get_eras():
    pre_ww1 = UK_athletes[UK_athletes['Year'] < 1914]
    between_wars = UK_athletes[(UK_athletes['Year'] >= 1914) & (UK_athletes['Year'] < 1945)]
    post_ww2_pre_1989 = UK_athletes[(UK_athletes['Year'] >= 1945) & (UK_athletes['Year'] < 1989)]
    post_1989 = UK_athletes[UK_athletes['Year'] >= 1989]
    return [pre_ww1, between_wars, post_ww2_pre_1989, post_1989]
