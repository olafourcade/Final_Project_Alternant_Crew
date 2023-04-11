import pandas as pd
import plotly.graph_objs as go
import json
import pandas as pd
import plotly.express as px
from dash import callback_context, dcc, html, Input, Output, State, Dash
import dash_bootstrap_components as dbc

global brand
brand = None


with open("us-county-boundaries.geojson") as f:
    geo_json_ = json.load(f)
if __name__ == "__main__":

    df = pd.read_csv("../Electric_Vehicle_Population_Data.csv")
    df["County"] = df["County"].astype("string")
    df = df[df["State"] == "WA"]  # The data is mainly for Washington state
    app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
    radio_items = dcc.RadioItems(id="brand", options=df["Make"].unique().tolist())
    ## Customize layout for out radio buttons ##
    brands = df["Make"].unique().tolist()
    brands_number = len(brands)
    grid = []
    number_col = 3
    number_row = brands_number // number_col
    if brands_number % number_col != 0:
        number_row += 1
    ### Loop to create the radio button grid layout ###
    for iRow in range(number_row):
        if iRow * number_col + number_col < brands_number:
            value = (
                "FORD"
                if "FORD" in brands[iRow * number_col : iRow * number_col + number_col]
                else None
            )
            margin_top = "70px" if iRow == 0 else "10px"
            radio_items = dcc.RadioItems(
                id=f"radio_button_{str(iRow)}",
                options=[
                    {"label": element, "value": element, "disabled": False}
                    for element in brands[
                        iRow * number_col : iRow * number_col + number_col
                    ]
                ],
                inline=True,
                value=value,
                style={
                    "font-size": "10px",
                    "padding-left": 10,
                    "margin-right": "10px",
                    "margin-top": margin_top,
                },
            )
        else:
            radio_items = dcc.RadioItems(
                id=f"radio_button_{str(iRow)}",
                options=[
                    {"label": element, "value": element, "disabled": False}
                    for element in brands[
                        iRow * number_col : iRow * number_col + number_col
                    ]
                ],
                inline=True,
                value=None,
                style={
                    "font-size": "10px",
                    "padding-left": 10,
                    "margin-right": "10px",
                    "margin-top": "10px",
                },
            )
        grid.append(dbc.Row([dbc.Col([radio_items], width=10)], justify="center"))

    geographical_figure = dcc.Graph(id="graph")
    choose_brand = dcc.Input(id="choose_brand", type="text", value="")
    ## Avoid that the user can choose more than one brand on the radio button grid ##
    @app.callback(
        [Output(f"radio_button_{str(i)}", "value") for i in range(number_row)],
        [Input("choose_brand", "value")]
        + [State(f"radio_button_{str(i)}", "value") for i in range(number_row)],
    )
    def check_only_one_radio_button(*value):

        choose_brand = value[0]
        states_value = value[1:]
        index_chosen_brand = [
            i for i, element in enumerate(states_value) if element == choose_brand
        ]
        ## return values for all radio buttons, None if the value is not the chosen brand ##
        if not index_chosen_brand:
            states_value = (
                [None, None] + ["FORD"] + [None for i in range(len(states_value) - 3)]
            )
            return (*states_value,)
        else:
            index_chosen_brand = index_chosen_brand[0]
            states_value = [
                None if i != index_chosen_brand else choose_brand
                for i in range(len(states_value))
            ]
            ## Reshape states_value to match the output of the callback ##
            print(f"state values {states_value}")
            return (*states_value,)

    ## Add a callback to update the geographical figure ##
    @app.callback(
        [Output("graph", "figure"), Output("choose_brand", "value")],
        [Input(f"radio_button_{str(i)}", "value") for i in range(number_row)],
    )
    def display_choropleth(*value):
        global brand
        active_value = [element for element in value if element and element != brand]
        value = active_value[-1] if active_value else None
        brand = value
        df_brand = df[df["Make"] == value]
        df_vehicle_per_county = (
            df_brand.groupby("County")
            .size()
            .reset_index(name="Number of electrical vehicles")
        )
        fig = px.choropleth(
            df_vehicle_per_county,
            geojson=geo_json_,
            color="Number of electrical vehicles",
            range_color=(
                0,
                df_vehicle_per_county["Number of electrical vehicles"].max(),
            ),
            featureidkey="properties.name",
            projection="mercator",
            locations="County",
            labels={"Number of electrical vehicles": "Number of electrical vehicles"},
        )

        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(
            title="Electric vehicles across Washington state", title_x=0.5
        )
        return fig, value

    ## Add an histogram of model for the selected brand ##
    histogram_model_brand = dcc.Graph(id="histogram_model_brand")
    ## Add a callback to update the histogram ##
    @app.callback(
        Output("histogram_model_brand", "figure"),
        [Input(f"radio_button_{str(i)}", "value") for i in range(number_row)],
    )
    def display_histogram(*value):
        global brand
        active_value = [element for element in value if element and element != brand]
        value = active_value[-1] if active_value else "FORD"
        brand = value
        df_brand = df[df["Make"] == value]
        df_model = (
            df_brand.groupby("Model").size().reset_index(name="Number of vehicles")
        )
        fig = px.bar(df_model, x="Model", y="Number of vehicles", color="Model")
        fig.update_layout(height=300, title="Model of electrical vehicles", title_x=0.5)
        return fig

    grid = dbc.Col(grid, width=4, id="radio_button_grid")
    map_col = dbc.Col([geographical_figure], width=8)
    row = dbc.Row([grid, map_col])
    row2 = dbc.Row(
        [dbc.Col([histogram_model_brand], width=8), dbc.Col([choose_brand], width=2)]
    )
    app.layout = dbc.Container([row, row2], fluid=True)
    app.run_server(debug=True)
