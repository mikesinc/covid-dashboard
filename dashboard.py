import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy

#COVID data imported (sourced from the daily dataset provided by Johns Hopkins University.)
confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
recovered_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
world_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv"
#convert to panda dataframes
world_df = pd.read_csv(world_url).to_numpy()
confirmed_df = pd.read_csv(confirmed_url, index_col='Province/State')
recovered_df = pd.read_csv(recovered_url, index_col='Province/State')
deaths_df = pd.read_csv(deaths_url, index_col='Province/State')

def get_entry_data(country="Australia", state=None):
    filtered_confirmed_df = confirmed_df[confirmed_df['Country/Region'] == country]
    filtered_recovered_df = recovered_df[recovered_df['Country/Region'] == country]
    filtered_deaths_df = deaths_df[deaths_df['Country/Region'] == country]
    if state:
        filtered_confirmed_df = filtered_confirmed_df[filtered_confirmed_df.index == state]
        filtered_recovered_df = filtered_recovered_df[filtered_recovered_df.index == state]
        filtered_deaths_df = filtered_recovered_df[filtered_recovered_df.index == state]
    return ({
        'confirmed': filtered_confirmed_df.T[4:],
        'recovered': filtered_recovered_df.T[4:],
        'deaths': filtered_deaths_df.T[4:]
        })

def get_totals(country="Australia", state=None):
    filtered_confirmed_df = confirmed_df[confirmed_df['Country/Region'] == country]
    filtered_recovered_df = recovered_df[recovered_df['Country/Region'] == country]
    filtered_deaths_df = deaths_df[deaths_df['Country/Region'] == country]
    country_totals = {
        'confirmed': filtered_confirmed_df.iloc[:,-1].sum(),
        'recovered': filtered_recovered_df.iloc[:,-1].sum(),
        'deaths': filtered_deaths_df.iloc[:,-1].sum()
    }
    if state:
        state_totals = {
            'confirmed': filtered_confirmed_df[filtered_confirmed_df.index == state].iloc[:,-1].sum(),
            'recovered': filtered_recovered_df[filtered_recovered_df.index == state].iloc[:,-1].sum(),
            'deaths': filtered_deaths_df[filtered_deaths_df.index == state].iloc[:,-1].sum()
        }
        return state_totals
    return country_totals

external_stylesheets = [dbc.themes.COSMO]
dropdown_menu_options = [{'label': item, 'value': item} for item in confirmed_df['Country/Region'].unique()]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "COVID-19 Global Dashboard"

banner = dbc.Jumbotron(
    [
        dbc.Container(
            [
                html.H1("Global COVID-19 Dashboard", className="display-3"),
                html.P(
                    "A country & state breakdown of COVID-19 total confirmed cases, recovered cases and deaths.",
                    className="lead",
                ),
                html.P(
                    "Enter a country and state (optional) below to view data.",
                    className="lead",
                ),
            ],
            fluid=True,
            style={'textAlign': 'center'}
        )
    ],
    fluid=True,
)

userInputs = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P(
                            "Country:",
                            className="lead",
                        ),
                        dcc.Dropdown(
                            id = "Country",
                            placeholder = "Select Country",
                            options = dropdown_menu_options,
                            className = "ml-5 mb-5",
                            value = 'Australia'
                        )
                    ]
                ),
                dbc.Col(
                    [
                        html.P(
                            "State/Province:",
                            className="lead",
                        ),
                        dcc.Dropdown(
                            id = "State",
                            placeholder = "Select State/Province",
                            className="ml-5 mb-5",
                        )
                    ]
                )
            ]
        )
    ]
)

results = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H2(
                                        "Total Confirmed Cases"
                                    ),
                                    html.H1(
                                        id="total_confirmed",
                                    )
                                ]
                            )
                        ],
                    style={"textAlign": "center"},
                    outline=True,
                    color="white"
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H2(
                                        "Total Recovered Cases"
                                    ),
                                    html.H1(
                                        id="total_recovered",
                                    )
                                ]
                            )
                        ],
                    style={"textAlign": "center"},
                    outline=True,
                    color="white"
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H2(
                                        "Total Deaths"
                                    ),
                                    html.H1(
                                        id="total_deaths",
                                    )
                                ]
                            )
                        ],
                    style={"textAlign": "center"},
                    outline=True,
                    color="white"
                    )
                ),
            ]
        )
    ],
    fluid=True
)

app.layout = html.Div([
    banner,
    userInputs,
    results
])

@app.callback(
    dash.dependencies.Output("State", "options"),
    [dash.dependencies.Input("Country", "value")]
)
def update_options(value):
    if not value:
        raise PreventUpdate
    return [{'label': option[6], 'value': option[6]} for option in world_df if value in option[7] and not str(option[6]) == 'nan']

@app.callback(
    dash.dependencies.Output("total_confirmed", "children"),
    [dash.dependencies.Input("Country", "value")],
    [dash.dependencies.Input("State", "value")]
)
def update_confirmed_cases(country_value, state_value):
    if not country_value:
        raise PreventUpdate
    if not state_value == "None":
        return get_totals(country=country_value, state=state_value)["confirmed"]
    return get_totals(country=country_value)["confirmed"]

@app.callback(
    dash.dependencies.Output("total_recovered", "children"),
    [dash.dependencies.Input("Country", "value")],
    [dash.dependencies.Input("State", "value")]
)
def update_recovered_cases(country_value, state_value):
    if not country_value:
        raise PreventUpdate
    if not state_value == "None":
        return get_totals(country=country_value, state=state_value)["recovered"]
    return get_totals(country=country_value)["recovered"]

@app.callback(
    dash.dependencies.Output("total_deaths", "children"),
    [dash.dependencies.Input("Country", "value")],
    [dash.dependencies.Input("State", "value")]
)
def update_deaths(country_value, state_value):
    if not country_value:
        raise PreventUpdate
    if not state_value == "None":
        return get_totals(country=country_value, state=state_value)["deaths"]
    return get_totals(country=country_value)["deaths"]

if __name__ == '__main__':
    app.run_server(debug=True)
