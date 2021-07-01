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


images = df.copy()
images['Details'] = images.apply(lambda x: x['Title'] + '\n  ' + x['Description'] + '\n  ' +x['Entry_ID'], axis=1)
images['image_url_thumbnail'] = images.apply(lambda x: x['Image_url'] + '#thumbnail', axis=1)
images['Photo'] = images.apply(lambda x: '![]({})'.format(x['image_url_thumbnail']), axis=1)
# images = images[['Photo','Details']]

# ----------------------------------------------------------------------------
# Create Gallery of Cards
# ----------------------------------------------------------------------------
df = images.head(10)
def build_gallery(df):
    # gallery = [html.P(Title) for Title in df['Details']]
    gallery = [
                html.Div([
                    html.Div(dcc.Markdown(photo)),
                    html.P(photo_title)
                ], className='gallery-card', id={'index': photo_index, 'type': 'image-card' })
        for photo_index, photo, photo_title  in zip(images['index'], images['Photo'], images['Title'])
    ]
    return gallery

# ----------------------------------------------------------------------------
# DASH APP LAYOUT
# ----------------------------------------------------------------------------
external_stylesheets_list = [dbc.themes.SANDSTONE] #  set any external stylesheets

app = dash.Dash(__name__,
                prevent_initial_callbacks=True,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                )

app.layout = html.Div([
    html.Div(id = 'testy'),
    html.H2("Pinpoint pictures on a Map"),
    # html.Div(children = build_gallery(df)),
    dbc.Row([
        dbc.Col([
            html.Div([
                    dt.DataTable(
                        id='table',
                        columns=[
                                 {'name': i, 'id': i,'type':'text' ,'presentation':'markdown'} for i in ('Photo','Details')
                                 # ,'presentation':'markdown'
                                 ],
                        data=images.to_dict('records'),
                        page_size= 5,
                         style_cell={
                         'whiteSpace': 'pre-line'
                         }
                    )
            ]),
            # html.Iframe(src="https://hub.catalogit.app/4837/folder/1d330100-93ce-11eb-9bd8-bb7a6aa1a9bb",
            # style={"height": "1067px", "width": "100%"})
        ],width = 3),
        dbc.Col([
            dl.Map([dl.TileLayer(), dl.LayerGroup(id="layer")],
                    center=[26.903, -98.158], zoom=8,
                   id="map",
                   style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"}),
           html.Div([
            html.P('''Look through the image gallery at left. If you find a picture where you know the location, click to enlarge,
            copy and paste the object ID into the box below, and select the location on the map above.'''),
            dcc.Input(id="input_object_ID",
                    type="text",
                    placeholder="Enter image Object ID"),
            html.Div(id='map_location'),
           ])
        ], width = 4),
    ]),

])


# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------

@app.callback([Output("layer", "children"),Output("map_location", "children")], [Input("map", "click_lat_lng")])
def map_click(click_lat_lng):
    if click_lat_lng is None:
        raise PreventUpdate
    else:
        new_layer_children = [dl.Marker(position=click_lat_lng, children=dl.Tooltip("({:.3f}, {:.3f})".format(*click_lat_lng)))]
        message = 'You have selected a point at {:.3f}, {:.3f}'.format(*click_lat_lng)
        return new_layer_children, message
# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True,port=8030)
else:
    server = app.server
