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
                html.H2("Sites & stories", className="display-4"),
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
                        'top' : 0,
                        'left' : 0,
                        'bottom' : 0,
                        'height' : '85%',
                        'width' : '16rem',
                        'padding' : '2rem 1rem',
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
                    html.Button('Button in form', id='btn_hide', n_clicks = 0)
                )
            ),
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
                        'TOBE: Submit Form',
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
        ])
    ],
    style = CONTENT_STYLE
)

app.layout = html.Div([sidebar,maindiv])

# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------

@app.callback(
    Output('testy','children'),
    Input('btn_hide','n_clicks'),
    Input({'type':'select_button','index': ALL}, 'n_clicks')
)
def show_box(hide_n_clicks, image_n_clicks):
    triggered = dash.callback_context.triggered[0]['prop_id'].replace('.n_clicks','')
    if triggered == 'btn_hide':
        return 'Hide the Input Form'
    else:
        return 'Show the Input Form'

@app.callback(
    Output('selected_image','children'),
    Input({'type':'select_button','index': ALL}, 'n_clicks'),
    State({'type':'select_button','index': ALL}, 'id'),
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
    [
        Input("map", "click_lat_lng")
    ]
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

# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True,port=8030)
else:
    server = app.server
