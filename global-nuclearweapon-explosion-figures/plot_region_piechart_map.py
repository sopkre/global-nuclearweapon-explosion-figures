#!/usr/bin/env python3.13

"""
Snippet to plot pie charts of explosion numbers and integrated yield in different world regions.

usage: plot_region_piechart_map.py [-h] -i INFILENAME -o OUTFILENAME -j COUNTRYREGIONJSON
"""

import plotly.graph_objects as go

import pandas as pd
import numpy as np

import argparse
import os.path

import helpers


def get_region_dict(jsonfile, key="cc"): 
    """Take data from json file to get map for states, country codes, and UN geoscheme regions. 
    Parameters
    ---------
        key : str 
            "cc", to get dict that maps country code to region; "region", to get dict that maps region name to list of states in that region.
        jsonfile : str
            filename for json file countainig the data
    """
    import json
    with open(jsonfile, 'rb') as f:
        jsonfile = json.load(f)

    region_dict = {}

    for j in jsonfile:
        cc = j['alpha-2']
        region = j['sub-region']
        name = j['name']

        if key=='cc':
            region_dict[cc] = region
        elif key=='region':
            if region not in region_dict:
                region_dict[region] = [name]
            else: 
                region_dict[region] += [name]

    return region_dict


def plot_regions(fig, df, jsonfile):
    """Highlight (outline, fill color) states belonging to the regions appearing in the dataframe.
    Parameters
    ---------
        fig : go.Figure 
            figure to plot regions on
        df : pd.DataFrame
            dataframe with regions that are plotted 
        jsonfile: str
            json file to create list of states that belong to region
    """
    import plotly.express as px
    colors = px.colors.qualitative.Set3[::-1]
    for i, region in enumerate([x for x in pd.unique(df["REGION"]) if x.find("Ocean")==-1]):
        plot_region(fig, region, jsonfile, color = colors[i], bordercolor="gray")


def plot_region(fig, region, jsonfile, color="lightblue", bordercolor="black"):
    """Highlight (outline, fill color) states belonging to a region. 
    Parameters
    ---------
        fig : go.Figure 
            figure to plot regions on
        region : str
            name of region to draw
        jsonfile: str
            json file to create list of states that belong to region
        color: str
            fill color of state
        bordercolor: str
            color of line around state
    """
    region_dict = get_region_dict(jsonfile, key="region")

    try: 
        fig.add_trace(go.Choropleth(
                locationmode = 'country names',
                locations = region_dict[region],
                z = [1 for _ in region_dict[region]],
                colorscale = [[0,color],[0.5, color], [1,color]],
                showscale = False,
                name = region,
                geo = 'geo1',
                marker={"line":{"width":1, "color":bordercolor}},
                legend = "legend3",
                visible = True,
                hovertemplate = '%{location}',
            )
        )
    except KeyError:
        print(f"[WARNING] Skipping {region}. ")



def add_pie_legend(fig, mode, visible, f):
    """Adds pie radius legend to the figure (via dummy pie charts)
    ---------
        fig : go.Figure
            figure to add legend to
        mode: str
            "number" for number of explosions, "yield" for summarized yield 
        visible: Bool
            whether legend is visible per default (can be switched via buttons)
        f: float
            factor to scale values for radius
    """

    values = []
    radii = []

    if mode.find("number") > -1:
        values = [50, 200, 300]
        text = values
    elif mode.find("yield") > -1:
        values = [10, 50, 100]
        text = [f"{int(t)}Mt" for t in values]

    radii = [v**(1/2)*f for v in values]

    LEGEND_X_POS = [0.75, 0.82, 0.917]
    LEGEND_Y_POS = [0.2, 0.2, 0.2]

    for i, val in enumerate(radii): 
        pie = go.Pie(
            domain_x = (LEGEND_X_POS[i]-radii[i], LEGEND_X_POS[i]+radii[i]), 
            domain_y = (LEGEND_Y_POS[i]-radii[i], LEGEND_Y_POS[i]+radii[i]),
            values=[values[i]],
            marker=dict(colors=["white"], line=dict(color='black', width=1)),
            textfont_size=15,
            textfont_color="black",
            textinfo='text',
            text = [text[i]],
            textposition='inside',
            visible=visible, 
            meta=mode, 
            showlegend=False, 
            hoverinfo='skip')
        fig.add_trace(pie)
    return fig


def plot_explosion_pies(fig, df, mode = "yield", visible=True):
    """Plots the pie chart for the chosen mode. Hacks go.Pie into map (position is given by figure fractions, size indicates total values)
    ---------
        fig : go.Figure
            figure to add legend to
        df : pd.DataFrame
            dataframe where locations are taken from
        mode: str
            "number" for number of explosions, "yield" for summarized yield 
        visible: Bool
            whether legend is visible per default (can be switched via buttons)
    """

    # Locations can only be set relative to figure (incl. random margins) bounds; set by hand.
    REGION_CENTRA_xy = { 
        'Northern America' : (0.13, 0.72),  
        'Central Asia' : (0.59, 0.71), 
        'Northern Africa' : (0.44, 0.64),  
        'Micronesia' : (0.85, 0.57),      
        'Eastern Europe' : (0.5, 0.76),
        'Eastern Asia' : (0.7, 0.65),  
        'Southern Asia' : (0.625, 0.59),  
        'Sub-Saharan Africa' : (0.45, 0.45),  
        'Australia and New Zealand' : (0.79, 0.38), 
        'South Atlantic Ocean' : (0.35, 0.38),
        'Arctic Ocean' : (0.5, 0.85),
        'North Pacific Ocean' : (0.94, 0.65),
        'Indian Ocean' : (0.6, 0.44)
        }
    fig.update_geos(projection=dict(type="equirectangular"))

    regions = df["REGION"].unique()
    # Sort list of regions by value to avoid the smaller pies hidden by the larger ones.
    N = [ len(df[(df.REGION==r)]) for (r) in regions ]
    regions = helpers.sort_list_by_score(regions, N)

    for i, region in enumerate(regions):
        df_r = df[df.REGION == region]
        states = []
        values = []
        # Factor to scale values to radius of pie chart. 
        f_radius = 1
        hovertemplate = ''
        for s in df_r.STATE.unique():
            states += [s]
            if mode.find("yield") > -1:
                values += [df_r[df_r.STATE==s]["YIELD"].sum()/1000] #mt
                f_radius = 0.00026*1000**(1/2)
                hovertemplate = '%{label}: <br> %{value:.3f} Mt'
            elif mode.find("number") > -1:
                values += [len(df_r[df_r.STATE == s])]
                f_radius = 0.004
                hovertemplate = '%{label}: <br> N = %{value}'
            else: 
                print("[WARNING] You need to specify the mode! (either 'yield' or 'number')!")

        R = np.sum(values)**(1/2)*f_radius

        (x,y) = REGION_CENTRA_xy[region]

        pie = go.Pie(
            labels=[helpers.FIXEDLABELS_[s] for s in states], 
            values=values,
            marker=dict(
                colors=[helpers.COLORS_[s] for s in states],
                line=dict(color='black', width=1)
            ),
            text = [f"{round(v/sum(values)*100)}%" if v/sum(values)>0.01 else "<1%" for v in values],
            hovertemplate = hovertemplate, 
            textfont_size=15,
            textfont_color="black",
            textinfo='text',
            domain_x = (x-R, x+R), 
            domain_y = (y-R, y+R),
            name = region,
            opacity=0.75, 
            visible=visible, 
            meta=mode
            )
        fig.add_trace(pie)

    add_pie_legend(fig, mode=mode, visible=visible, f=f_radius)
    return fig


def update_layout(fig):
    """Set the different layout choices. 
    ---------
        fig : go.Figure
            figure to add legend to
    """
    legend_dict = {
        'legend1' : {
            'yanchor' : "top",
            'y' : 1.02,  
            'xanchor' : "left",
            'x' : 0.0, 
            'font' : {'size' : 15},
            'orientation' : 'h',
            'borderwidth' : 1,
            'itemsizing' : 'constant',
            },
        'showlegend': True,
    }

    layout_dict = dict(
        dragmode=False,
        modebar_remove=['lasso', 'zoom', 'zoom in', "box select", "pan"], 
        margin={"r":0,"t":16*3,"l":0,"b":0, "autoexpand": False},
        height=600, 
        width=16*55, # 16/em; 55em = fit for website
        map_zoom = 0,
        geo1 = dict(
            countrywidth = 0,
            resolution = 50, #50?
            projection=dict(type="equirectangular"), 
            lataxis_showgrid=True, lonaxis_showgrid=True
        ))

    fig.update_geos(
        lataxis_range=[-90, 90], lonaxis_range=[-140, 210],
        projection=dict(type="equirectangular")
    )

    fig.update_layout(
        layout_dict
    )

    fig.update_layout(
        legend_dict
    )


def add_buttons(fig, mode_label_dict):
    """Add the buttons to switch between "number" and "yield" plot. 
    ---------
        fig : go.Figure
            figure to add legend to
        mode_label_dict : dict
            keys: mode to add (e.g. "yield"), values: title for respecive button
    """
    region_traces = [isinstance(f, go.Choropleth) for f in fig.data ]
    
    traces = []
    modes = []
    for mode in mode_label_dict:
        traces += [ [f.meta==mode for f in fig.data] ]
        modes += [mode]
        print(f"[INFO] Added {mode} to legend!")

    buttons = []
    for i, t in enumerate(traces):
        buttons += [dict(label=mode_label_dict[modes[i]],
            method="update",
            args=[{"visible": [ x | y for (x,y) in zip(region_traces, t)]}] 
            )]

    menu_dict = {'updatemenus' : [
        dict(
            type="buttons",
            direction="right",
            active=0,
            x=0.01,
            y=0.11,
            xanchor='left', 
            yanchor='bottom', 
            buttons=buttons,
            font_size=15
        )
    ]}

    fig.update_layout(
        menu_dict
    )


def main(infilename, outfilename, country_region_json):
    """Main. 
    Parameters
    ---------
        infilename : str 
            filename of pickled pd.Dataframe with explosion locations
        outfilename : str
            filename for pickled go.Figure
    """
    
    df = helpers.load_pkl(infilename)
    df = df.drop(df[df.LAT.isnull()].index)

    if not os.path.isfile(country_region_json):
        input(f"[WARNING] Json that connects states to regions does not exist. Will download it and save it as '{country_region_json}'. Press enter to continue...")
        import urllib.request
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/refs/heads/master/all/all.json", 
            country_region_json
        )

    # Plotting
    # --------

    fig = go.Figure()

    plot_regions(fig, df, country_region_json)
    plot_explosion_pies(fig, df, "number")
    # plot_explosion_pies(fig, df[df.TYPE.str.contains("A")], "yield_A", visible=False)
    # plot_explosion_pies(fig, df[df.TYPE.str.contains("UG") | df.TYPE.str.contains("UW") ], "yield_UG", visible=False)
    plot_explosion_pies(fig, df, "yield", visible=False)

    add_buttons(fig, 
        {"number": "Exlosion number", 
        "yield": "Explosion yield", 
        # "yield_A" : "Yield atmospheric", 
        # "yield_UG" : "Yield underground/-water"
        }
    )

    update_layout(fig)

    # Save output
    # -----------

    if outfilename.find(".html") > -1:
        fig.write_html(outfilename)
        print(f"[INFO] Saved figure as {outfilename}.")
    elif outfilename.find(".pkl") > -1:
        helpers.save_pkl(fig, outfilename)
        print(f"[INFO] Saved figure as {outfilename}.")
    else: 
        print("[ERROR] You can save the figure only as .html or .pkl file.")
        fig.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="input data in pandas dataframe", required=True)
    parser.add_argument("-o", "--outfilename", help="output file, either html or pkl format.", required=True)
    parser.add_argument("-j", "--countryregionjson", help="json that maps states to region. If file does not exist, it is downloaded there.", required=True)
    args = parser.parse_args()

    main(args.infilename, args.outfilename, args.countryregionjson)

