import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

athlete_events = pd.read_csv("Render_Deploy/src/data/athlete_events.csv")
UK_athletes = athlete_events[athlete_events['NOC'] == 'GBR']

def prepare_data_and_plots():
    pre_ww1 = UK_athletes[UK_athletes['Year'] < 1914]
    between_wars = UK_athletes[(UK_athletes['Year'] >= 1914) & (UK_athletes['Year'] < 1945)]
    post_ww2_pre_2000 = UK_athletes[(UK_athletes['Year'] >= 1945) & (UK_athletes['Year'] < 2000)]
    post_2000 = UK_athletes[UK_athletes['Year'] >= 2000]
    
    fig_all = make_subplots(subplot_titles=(
 
    ))
    
    fig_all.add_trace(go.Histogram(x=pre_ww1['Age'], nbinsx=50, name="< 1914, Age Distribution of UK's Athletes"))
    fig_all.add_trace(go.Histogram(x=between_wars['Age'], nbinsx=50, name="1914-1940, Age Distribution of UK's Athletes between WWI & WWII" ))
    fig_all.add_trace(go.Histogram(x=post_ww2_pre_2000['Age'], nbinsx=50, name="1945 - 2000, Age Distribution of UK's Athletes After WWII"))
    fig_all.add_trace(go.Histogram(x=post_2000['Age'], nbinsx=50, name="2000 Onwards, Age Distribution of UK's Athletes"))

    fig_all.update_layout(title_text="Age Distribution of UK's Athletes Across Different Eras",
                          xaxis_title_text="Age",
                          yaxis_title_text="Number of Athletes",
                          bargap=0.02,
                          bargroupgap=0.01,
                          hovermode="x unified")

    return fig_all

# UK seasonal grafen


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
                      xaxis_tickangle=-45,
                      )
    return fig

def age_data():
    df_age = UK_athletes[['Age', 'Name']].groupby(['Name', 'Age']).count().reset_index()
    fig = px.histogram(df_age, x='Age', title="Age distribution UK's Data")
    fig.update_layout(hovermode="x unified")
    return fig
