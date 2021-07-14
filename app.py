# ----------------------------------------------------------------------------
# PYTHON LIBRARIES
# ----------------------------------------------------------------------------

# File Management
import os # Operating system library
import pathlib # file paths

# Data Cleaning and transformations
import pandas as pd
import numpy as np
# import requests
from datetime import datetime
from dateutil import tz
import json

# Data visualization
import plotly.express as px
import plotly.graph_objects as go

# Dash Framework
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import dash_leaflet as dl
import dash_daq as daq
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash.exceptions import PreventUpdate


# ----------------------------------------------------------------------------
# CONFIG SETTINGS
# ----------------------------------------------------------------------------
ASSETS_PATH = pathlib.Path(__file__).parent.joinpath("assets")

# ----------------------------------------------------------------------------
# Data Loadind
# ----------------------------------------------------------------------------
images_file = 'mosth-beulah-metadata.csv'
df = pd.read_csv(os.path.join(ASSETS_PATH, images_file))
# df['md_html'] = '<img src="' + df['Image'] + '" alt="'+ df['Description'] + '" title="'+ df['Description'] + '" width="150" height="100" />'

# Get dataframe with images information for display
images = df.copy()
images['Details'] = images.apply(lambda x: x['Title'] + '\n  ' + x['Description'] + '\n  ' +x['Entry_ID'], axis=1)
images['image_url_thumbnail'] = images.apply(lambda x: x['Image_url'] + '#thumbnail', axis=1)
images['Photo'] = images.apply(lambda x: '![]({})'.format(x['image_url_thumbnail']), axis=1)
# images = images[['Photo','Details']]

# index image data by entry ID
image_search = df.set_index('Entry_ID')

# ----------------------------------------------------------------------------
# Create Gallery of Cards
# ----------------------------------------------------------------------------
df10 = images.head(10)
#df10 = images
def build_gallery(df):
    # gallery = [html.P(Title) for Title in df['Details']]
    image_list = [
         (entry_id, photo, photo_title)
         for entry_id, photo, photo_title
         in zip(df['Entry_ID'], df['Photo'], df['Title'])
    ]
    gallery = [
        html.Div(
            [
                html.Div(dcc.Markdown(photo)),
                html.Div(photo_title),
                html.Button(
                    entry_id,
                    id = {'index' : entry_id, 'type' : 'select_button'},
                    n_clicks = 0
                )
            ],
            className = 'gallery-card',
            id = {'index' : entry_id, 'type' : 'image-card'},
            n_clicks = 0
        )
        for i, (entry_id, photo, photo_title)
        in enumerate(image_list)
    ]
    return gallery

# ----------------------------------------------------------------------------
# DASH APP LAYOUT
# ----------------------------------------------------------------------------
external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = dash.Dash(
    __name__,
    prevent_initial_callbacks = True,
    external_stylesheets = external_stylesheets_list,
    meta_tags = [{
        'name' : 'viewport',
        'content' : 'width=device-width, initial-scale=1'
    }],
    suppress_callback_exceptions = True
)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/lexus'

SIDEBAR_STYLE = {
    "position" : "fixed",
    "top" : 0,
    "left" : 0,
    "bottom" : 0,
#   width = 12
    "width" : "16rem",
    "padding" : "2rem 1rem",
    "background-color" : "#f8f9fa"
}

CONTENT_STYLE = {
    "margin-left" : "18rem",
    "margin-right" : "2rem",
    "autosize" : "True",
#    'margin' : '15px',
    "padding" : "2rem 1rem",
    "display" : "inline-block",
#    'border' : '1px solid blue'
}

sidebar = html.Div(
    [
        dbc.Col([
            dbc.Row(
                html.H2("Sites & Stories", className="display-4"),
        #        html.Hr(),
        #        html.Div('Testy!', id='testy'),
        #        html.P(
        #            "A simple sidebar", className="lead"
        #        ),
            ),
            dbc.Row(
                html.Div(
                    build_gallery(df10),
                    style = {
                        'position' : 'fixed',
#                        'top' : 0,
                        'left' : 0,
                        'bottom' : 0,
                        'height' : '85%',
                        'width' : '16rem',
                        'padding' : '4rem 1rem',
                        'overflow' : 'scroll',
                        'overflowY' : 'scroll'
                    }
                )
            )
        ])
    ],
    style = SIDEBAR_STYLE
)

maindiv = html.Div(
#    id = "first-div",
    id = 'data-entry=form',
    children = [
        html.Div([
            dbc.Row(
                dbc.Col(
                    [
                        dl.Map(
                            [dl.TileLayer(), dl.LayerGroup(id="layer")],
                            center = [26.903, -98.158],
                            zoom = 8,
                            id = "map",
                            style = {
#                                'width' : '85%',
                                'width' : '60vw',
                                'height' : '43vh',
                                'margin' : "auto",
                                "display" : "block"
                            }
                        ),
                        html.Div(id='map_location')
                    ]#,
#                    width='85%'
                ),
                id = 'data_entry'
            ),
            dbc.Row(
                dbc.Col(
                    html.Button(
                        'Submit',
                        id = 'btn_submit',
                        n_clicks = 0
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    [
                        html.Div(
                            id = 'selected_image'
                        )
                    ]
                )
            )
        ]),
        html.Footer([
            dbc.Row([
                dbc.Col(
                    html.Img(
                        src = app.get_asset_url('Logo-MOSTH.png'),
                        style = {
                            'height' : '70px'
                        }
                    )
                ),
                dbc.Col(
                    html.Img(
                        src = app.get_asset_url('Logo-PT2050.png'),
                        style = {
                            'height' : '70px'
                        }
                    )
                ),
                dbc.Col(
                    html.Img(
                        src = app.get_asset_url('Logo-Azure.png'),
                        style = {
                            'height' : '70px'
                        }
                    )
                ),
                dbc.Col(
                    html.Img(
                        src = app.get_asset_url('Logo-NSF.png'),
                        style = {
                            'height' : '70px'
                        }
                    )
                )
            ]),
            dbc.Row(
                dbc.Col([
                    html.P("This work is a collaboration between the Museum of South Texas and the Planet Texas 2050 project with sponsorship from"),
                    html.Ul(children = [
                        html.Li("The National Science Foundation Smart & Connected Cities program (award number 1952196)"),
                        html.Li("Microsoft Azure Intersectionality and Equity program"),
                        html.Li("The Planet Texas project of the Bridging Barriers Program at The University of Texas at Austin"),
                        html.Li("Navigating the New Arctic program (Award Number (FAIN): 2127353)")
                    ])
                ])
            ),
            dbc.Row(
                dbc.Col(
                    html.Button(
                        'Explanation of work',
                        id = 'btn_poster',
                        n_clicks = 0
                    )
                )
            )
        ])
    ],
    style = CONTENT_STYLE
)

popup = dbc.Modal(
    [
        dbc.ModalHeader("Input form"),
        dbc.ModalBody(
            [
                dbc.Label("Timestamp:"),
                dbc.Input(
                    id = "liveview_label_datetime",
                    type = "text",
                    disabled = True
                ),
                dbc.Label("Image ID:"),
                dbc.Input(
                    id = "liveview_label_image",
                    type = "text",
                    disabled = True
                ),
                dbc.Label("Coordinates:"),
                dbc.Input(
                    id = "liveview_label_coordinates",
                    type = "text",
                    disabled = True
                )
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit",
                    color = "primary",
                    id = "liveview_modal_ok_button"
                ),
                dbc.Button("Cancel", id="liveview_modal_cancel_button")
            ]
        )
    ],
    id = "liveview_label_modal"
)

popup_initial = dbc.Modal(
    [
        dbc.ModalHeader("Intro"),
        dbc.ModalBody(
            [
                html.P(
                    "The Sites & Stories application allows users to select a photograph and connect it with where they think it’s located on a map. Additionally, people can add comments and describe what they know about the image or location."
                ),
                html.P(
                    "By providing your data, information, and experiences with events in your region, you will contribute to an effort to make more informed decisions about how to respond to and prepare for disasters. The stories or comments you make on photographs will help improve tools we use to model where flooding may impact communities."
                ),
                html.P(
                    "Data collected during the study will be stored, maintained, and made accessible within the Texas Disaster Information System (TDIS). TDIS will be an interactive web-based spatial data system to support disaster preparedness, response, recovery, and mitigation within communities and regions across the State of Texas. TDIS will comply with state and federal information and data security requirements and will provide powerful analytical and planning tools for local communities."
                )
            ]
        ),
        dbc.ModalFooter(
            dbc.Button(
                "OK",
                color = "primary",
                id = "liveview_modal_ok_button_initial"
            )
        )
    ],
    id = "liveview_label_modal_initial"
)

popup_poster = dbc.Modal(
    [
        dbc.ModalHeader("Poster"),
        dbc.ModalBody(
            html.Img(
                src = app.get_asset_url('Poster.png'),
                style = {
                    'height' : '85vh',
                    'width' : '85vw'
                }
            )
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Close",
                color = "primary",
                id = "liveview_modal_close_button"
            )
        )
    ],
    id = "liveview_label_modal_poster"
)

app.layout = html.Div([
    dcc.Location(id='url',refresh=False),
    sidebar,
    maindiv,
    popup_initial,
    popup,
    popup_poster
])

# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------

@app.callback(
    Output('testy','children'),
    [
        Input('btn_hide','n_clicks'),
        Input({'type':'select_button','index': ALL}, 'n_clicks')
    ]
)
def show_box(hide_n_clicks, image_n_clicks):
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    if triggered == 'btn_hide':
        return 'Hide the Input Form'
    else:
        return 'Show the Input Form'

@app.callback(
    Output('selected_image','children'),
    Input({'type':'image-card','index': ALL}, 'n_clicks'),
    State({'type':'image-card','index': ALL}, 'id')
)
def show_box(n_clicks, entry_id):
    # get index of clicked image
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    trigger = json.loads(triggered)
    trigger_index = trigger['index']
    # get image url from image
    image_url = image_search.at[trigger_index,'Image_url']
    kids = html.Div(
        html.Img(
            src = image_url,
            style = {
                'width' : '60vw'
            }
        )
    )
    return kids #"{}".format(image_url)

@app.callback(
    [
        Output("layer", "children"),
        Output("map_location", "children")
    ],
    Input("map", "click_lat_lng")
)
def map_click(click_lat_lng):
    if click_lat_lng is None:
        raise PreventUpdate
    else:
        new_layer_children = [
            dl.Marker(
                position = click_lat_lng,
                children = dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng))
            )
        ]
        message = 'You have selected a point at {:.3f}, {:.3f}'.format(*click_lat_lng)
        return new_layer_children, message

@app.callback(
    [
        Output("liveview_label_modal", "is_open"),
        Output("liveview_label_datetime", "value"),
        Output("liveview_label_image", "value"),
        Output("liveview_label_coordinates", "value")
    ],
    [
        Input("btn_submit", "n_clicks"),
        Input("liveview_modal_ok_button", "n_clicks"),
        Input("liveview_modal_cancel_button", "n_clicks"),
        Input({'type':'select_button','index': ALL}, 'n_clicks'),
        Input("map", "click_lat_lng")
    ],
    [
        State("liveview_label_modal", "is_open"),
        State("liveview_label_datetime", "value"),
        State({'type':'select_button','index': ALL}, 'id')
    ]
)
def show_modal(
    n_add : int,
    n_ok : int,
    n_cancel : int,
    n_clicks,
    click_lat_lng,
    is_open : bool,
    dt: str,
    entry_id
):
    """
    Show modal for adding a label.
    https://community.plotly.com/t/does-dash-support-a-input-form-popup/42482
    """
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    if triggered == "btn_submit":
        return True, dt, entry_id, click_lat_lng
    if triggered == "liveview_modal_ok_button":
        dt_local = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").astimezone()
        dt_utc = dt_local.astimezone(tz.UTC)
#        db_client.create_label(
#            dt_utc,
#            entry_id,
#            click_lat_lng,
#            redis_client.get(REDIS_RECORDING.key)
#        )
        return False, dt, entry_id, click_lat_lng
    return False, dt, entry_id, click_lat_lng

@app.callback(
    Output("liveview_label_modal_initial", "is_open"),
    [
        Input("url", "pathname"),
        Input("liveview_modal_ok_button_initial", "n_clicks")
    ],
    State("liveview_label_modal_initial", "is_open")
)
def display_page(
    pathname,
    n_ok : int,
    is_open : bool,
):
    """Show modal for adding a label."""
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    if triggered == "liveview_modal_ok_button_initial":
        return False
    return True

@app.callback(
    Output("liveview_label_modal_poster", "is_open"),
    [
        Input("btn_poster", "n_clicks"),
        Input("liveview_modal_close_button", "n_clicks")
    ],
    State("liveview_label_modal_poster", "is_open")
)
def display_page(
    n_add : int,
    n_close : int,
    is_open : bool,
):
    """Show modal for adding a label."""
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    if triggered == "btn_poster":
        return True
    if triggered == "liveview_modal_close_button":
        return False
    return False

# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True,port=8030)
else:
    server = app.server
