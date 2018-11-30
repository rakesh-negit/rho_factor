import os
import time
from textwrap import dedent

import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
from dash.dependencies import Input, Output, State

import visu.process as pr
import visu.dash_reusable_components as drc
from visu.figures import serve_prediction_plot, serve_roc_curve, \
    serve_pie_confusion_matrix

rho = pr.rho()
rho.load_rho_lut()
df = rho.rho

button = []
for lev in df.index.levels:
    min, max = lev.values.min(), lev.values.max()
    button.append(
        drc.NamedSlider(
            name=f'{lev.name} range',
            id='slider-dataset-sample-size',
            min=min,
            max=max,
            step=((max - min) / 5),
            marks={i: i for i in lev.values},
            value=min
        ), )

DDButton = []
ids = []
for lev in df.index.levels:
    v = lev.values
    v0=v[0]
    if lev.name == 'wl':
        v0=v
    id_ = 'dd_' + lev.name
    ids.append(id_)
    DDButton.append(
        drc.NamedDropdown(
            name=f'{lev.name} range',
            id=id_,
            options=[{'label': str(i), 'value': i} for i in v],
            value=v0,
            multi=True
        ), )

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    # .container class is fixed, .container.scalable is scalable
    html.Div(className="banner", children=[
        # Change App Name here
        html.Div(className='container scalable', children=[
            # Change App Name here
            html.H2(html.A(
                'Surface reflection factor',
                href='https://github.com/Tristanovsk/rho_factor',
                style={
                    'text-decoration': 'none',
                    'color': 'inherit'
                }
            )),

            html.A(
                html.Img(
                    src="https://github.com/Tristanovsk/rho_factor/blob/master/fig/lut_fig_rho_tables_wl550.0nm_aot0.0001.png"),
                href='https://plot.ly/products/dash/'
            )
        ]),
    ]),

    html.Div(id='body', className='container scalable', children=[
        html.Div(className='row', children=[
            html.Div(
                id='div-graphs',
                children=dcc.Graph(
                    id='main_graph',
                    style={'display': 'none'}
                )
            ),

            html.Div(
                className='three columns',
                style={
                    'min-width': '24.5%',
                    'max-height': 'calc(100vh - 85px)',
                    'overflow-y': 'auto',
                    'overflow-x': 'auto',
                },
                children=[
                    drc.Card(html.Div(DDButton))
                ]),

        ]),
        html.Div(
            dcc.Markdown(dedent("""
                [Click here](https://github.com/Tristanovsk/rho_factor) to visit the project repo, and learn about how to use the app.
                """)),
            style={'margin': '20px 0px', 'text-align': 'center'}

        ),

    ]),

])


def figure(dff,levels,col):
    layout = go.Layout(xaxis={'title': 'Wavelength (nm)'},
                   yaxis={'title': 'test'},
                   hovermode='closest')
    trace = []
    for idx, data  in dff.groupby(level=levels):
        print(idx)
        trace.append(go.Scattergl(
            x=data.index.get_level_values(2),  # spectrum,
            y=data.iloc[:,col],
            text=data.index.get_level_values(0),

            mode='lines+markers',
            marker={
                'size': 7,
                'opacity': 0.5,
                 #'color': 'rgba({}, {}, {}, {})'.format(*s_m.to_rgba(parameters[i]).flatten()),
                # x.unique(),#color': df.index.get_level_values(0),
                'line': {'width': 0.5, 'color': 'white'},
            },
            #line=go.scatter.Line()#color=rgba({}, {}, {}, {})'.format(*s_m.to_rgba(parameters[i]).flatten()), width=2),
        ))


    # spectrum = df[label['aod']].stack()
    return {
        'data': trace,
        'layout': layout
    }

input = []
for id_ in ids:
    input.append(Input(id_, 'value'))


@app.callback(Output('div-graphs', 'children'),
              input)
def update_svm_graph(*kargs):
    print(kargs)
    dff = df.loc[kargs]
    levels=[0, 1, 3, 4, 5] #range(dff.index.levels.__len__())
    return [


        html.Div(
            className='nine columns',
            style={'margin-top': '5px',
                   },
            children=[
                dcc.Graph(
                    id='main_graph',
                    figure=figure(dff,levels, 0),
                    style={'height': '50%'}
                ),
                dcc.Graph(
                    id='main_graph2',
                    figure=figure(dff, levels, 1),
                    style={'height': '50%'}
                )
            ]),

    ]


external_css = [
    "https://rawgit.com/xhlulu/9a6e89f418ee40d02b637a429a876aa9/raw/f3ea10d53e33ece67eb681025cedc83870c9938d/base-styles.css"
]
#
for css in external_css:
    app.css.append_css({"external_url": css})

# Running the server
if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server()
