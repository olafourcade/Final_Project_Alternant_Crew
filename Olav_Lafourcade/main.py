from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go



# creating the data frame

df = pd.read_csv('../Electric_Vehicle_Population_Data.csv')
df_range = df.iloc[:,[5,6,7,8, 10]]



model_list = df["Model"].unique().tolist()
make_list = df['Make'].unique().tolist()

# Define the options for the color representation RadioItems component
color_representation_options = [
    {'label': 'Continuous', 'value': 'continuous'},
    {'label': 'Discrete', 'value': 'discrete'}
]

# Define the options for the years RadioItems component
year_list = [2016,2017,2018, 2019, 2020, 2021,2022,2023]
year_radioitems_options = [{'label': str(year), 'value': year} for year in year_list]

app = Dash(__name__)


app.layout = html.Div([
    # Add the RadioItems component for car makers
    dcc.RadioItems(
        id='make-radioitems',
        options=[{'label': make, 'value': make} for make in make_list],
        value=make_list[7],
        labelStyle={'display': 'inline-block'},
        style={
            "font-size": "10px",
            "padding-left": 10,
            "margin-right": "10px",
            "margin-top": "10px",
        }
    ),
    # Add the RadioItems component for color representation selection
    dcc.RadioItems(
        id='color-representation-radioitems',
        options=color_representation_options,
        value='continuous',
        labelStyle={'display': 'inline-block'},
        style={
            "font-size": "10px",
            "padding-left": 10,
            "margin-right": "10px",
            "margin-top": "10px",
        }
    ),
    
    # Add the scatter plot figure for car makers
    dcc.Graph(id='scatter-plot'),
    
    
    dcc.RadioItems(
            id='year-radioitems',
            options=year_radioitems_options,
            value=year_list[3],
            labelStyle={'display': 'inline-block'},
            style={
                "font-size": "10px",
                "padding-left": 10,
                "margin-right": "10px",
                "margin-top": "10px",
            }
    ),

    # # Add the scatter plot figure for car makers
    # dcc.Graph(id='scatter-plot'),
    # Add the scatter plot figure for years
    dcc.Graph(id='year-plot')

])



@app.callback(
    Output('scatter-plot', 'figure'),
    [
        Input('make-radioitems', 'value'),
        Input('color-representation-radioitems', 'value')
    ]
)


def update_scatter_plot(make, color_representation):
    df_make = df_range[df_range['Make'] == make]
    df_make = df_make[df_make["Electric Range"] > 0]
    car_constructor = df_make['Make'].iloc[0]
    
    if color_representation == 'continuous':
        df_make['Model Year'] = df_make['Model Year'].astype(float)
        
    else:
        df_make['Model Year'] = df_make['Model Year'].astype(str)

    
    fig = px.scatter(df_make, x="Model", y="Electric Range",
                    color="Model Year", hover_name="Model", color_continuous_scale='YlGn')
    fig.update_traces(marker=dict(size=15))
    fig.update_layout(
        title="Evolution of {}'s electric vehicle".format(car_constructor),
        xaxis_title="Car Model",
        yaxis_title="Electric Range in Miles",
        title_x=0.5
    )
    return fig


@app.callback(
    Output('year-plot', 'figure'),
    Input('year-radioitems', 'value'),
)


def update_year_plot(year):
    df_year = df_range[df_range['Model Year'] == year]
    l = df_year['Electric Range'].unique()
    max_values = sorted(l, reverse=True)    
    list_model = []
    value = []
    for i in range(3):
        if year == 2020:
            list_model = ['MODEL S', 'MODEL 3', 'MODEL X']
            value = [337, 322, 293]

        else:
            list_model.append(df_year[df_year['Electric Range'] == max_values[i]].iloc[0,2])
            value.append(df_year[df_year['Electric Range'] == max_values[i]].iloc[0,4])
        
    # fig = go.Figure(data=[go.Scatter(
    #     x=list_model, y=value,
    #     mode='markers',
    #     marker_size=[100,75,60])]) 
    
    fig = go.Figure()

    # Add scatter plot trace
    fig.add_trace(
        go.Scatter(
            x=list_model,
            y=value,
            mode='markers',
            marker_size = [100,75,60],
        )
    )
                          
    fig.update_layout(
        title="Top 3 electric vehicles in terms of range in {}'s ".format(year),
        xaxis_title="Car Model",
        yaxis_title="Electric Range in Miles",
        title_x=0.5
    )
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)