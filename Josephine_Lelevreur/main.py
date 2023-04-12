# -*- coding: utf-8 -*-
"""DV_Assignment3_dash.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1n6C7_jlhEb2lUCF7JYUwKa04bgmP-0QC

We seek to understand the relationship between the type of technologies for the car models used and the counties in which they are used.We also want to see the impact that the Clean Alternative Fuel Vehicle (CAFV) Eligibility.
"""

import pandas as pd
import plotly.graph_objs as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px


# Load CSV data
df = pd.read_csv("../Electric_Vehicle_Population_Data.csv")

# Define options for the eligibility dropdown
eligibility_options = [
    'Clean Alternative Fuel Vehicle Eligible',
    'Not eligible due to low battery range',
    'Eligibility unknown as battery range has not been researched',
    'All eligibilities combined'
]

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='eligibility-dropdown',
        options=[{'label': option, 'value': option} for option in eligibility_options],
        value=eligibility_options[-1]
    ),
    dcc.Graph(id='graph-output')
])

@app.callback(
    dash.dependencies.Output('graph-output', 'figure'),
    [dash.dependencies.Input('eligibility-dropdown', 'value')]
)
def update_graph(eligibility):
    
    if eligibility == 'All eligibilities combined':
        selected_df = df
    else:
        selected_df = df[df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'] == eligibility]
        
    pivot_df = pd.pivot_table(selected_df, values='VIN (1-10)', index='County', columns='Electric Vehicle Type', aggfunc='count')
    
    if pivot_df.shape[1] == 1:
        pivot_df['Plug-in Hybrid Electric Vehicle (PHEV)'] = pd.Series([0] * len(pivot_df))
        
    filtered_df = pivot_df.loc[(pivot_df['Battery Electric Vehicle (BEV)'] >= 500) | (pivot_df['Plug-in Hybrid Electric Vehicle (PHEV)'] >= 500)]
    fig = px.bar(filtered_df, barmode='stack')
    fig.update_layout(
        title='Distribution of electric vehicle types by County',
        xaxis_title='County',
        yaxis_title='Number of electric vehicles'
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=False)

"""To conclude, in general, we see that the preferred models in all counties are Battery Electric Vehicles (BEV). This is especially true for cars meeting Clean Alternative Fuel Vehicle (CAFV) eligibility. On the other hand, cars that are not eligible due to low battery range, are exclusively Plug-in Hybrid Electric Vehicle (PHEV) technology. Cars with unknown eligibility as battery range has not been researched, have exclusively Battery Electric Vehicle (BEV) technology."""