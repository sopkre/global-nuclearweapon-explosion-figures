#!/usr/bin/env python3.13

"""
Code snippet to plot nuclear explosions on map.

usage: plot_explosion_locations.py [-h] -i INFILENAME -o OUTFILENAME
"""

import argparse

import plotly.graph_objects as go
import numpy as np

import pandas as pd

import helpers 

def make_location_frequency_df(df): 
    """Makes dataframe with locations and frequency. 
    Parameters
    ---------
        df : pd.Dataframe
            Dataframe with list of locations. 
    """

    print("[INFO] Creating explosion location dataframe... ")

    df['coords'] = [ t for t in zip(df.LAT, df.LONG) ]

    dff = pd.DataFrame(df['coords'].value_counts())
    dff = dff.rename_axis('coords').reset_index()
    dff = dff.rename(columns={"count": "COUNT"})

    dff["LAT"] = (dff['coords']).str[0]
    dff["LONG"] = (dff['coords']).str[1]

    for coord in dff.coords:

        df_at_coord = df[df['coords']==coord]

        # set state 
        assert "[WARNING] MORE STATES TESTED AT ONE LOCATION!", len(df_at_coord["STATE"].unique()) == 1 
        state = df_at_coord["STATE"].iloc[0]        
        dff.loc[dff['coords']==coord, "STATE"] = state

        # set yield range at location
        yields_at_coord = list(df_at_coord["YIELD"])
        dff.loc[dff['coords']==coord, "YIELD"] = helpers.make_range_string(yields_at_coord)

        # set year range at location
        years_at_coord = list(df_at_coord["YEAR"])
        dff.loc[dff['coords']==coord, "YEAR"] = helpers.make_range_string(years_at_coord)

        # set list of names at location
        shotnames = [ x if x is not None else "n/a" for x in df_at_coord["SHOTNAME"].to_list()]
        shotnames = (", ".join(shotnames))
        shotnames = helpers.add_breaks(shotnames, 10)
        dff.loc[dff['coords']==coord, "SHOTNAME"] = shotnames

        # explosion type and delivery
        assert "[WARNING] MORE EXPLOSTION TYPES AT ONE LOCATION!", len(df_at_coord["TYPE"].unique()) == 1 
        explosion_type = df_at_coord["TYPE"].iloc[0]        
        dff.loc[dff['coords']==coord, "TYPE"] = helpers.TYPESLABEL_[helpers.get_part_before_hyphen(explosion_type)]
        dff.loc[dff['coords']==coord, "DELIVERY"] = helpers.DELIVERYLABEL_[helpers.get_part_after_hyphen(explosion_type)]

        # purpose
        assert "[WARNING] MORE EXPLOSTION PURPOSES AT ONE LOCATION!", len(df_at_coord["PUR"].unique()) == 1 
        p = df_at_coord["PUR"].iloc[0]
        if (type(p) is float and np.isnan(p)):
            p = "n/a"
        else:
            p = helpers.PURPOSELABEL_[df_at_coord["PUR"].iloc[0]]
        dff.loc[dff['coords']==coord, "PUR"] = p

    print("[INFO] ... Done!")

    return dff         


def draw_density(fig, df): 
    """Draw test density at location
    Parameters
    ---------
        fig : go.Figure
            Figure to draw the density plot on
        df : pd.Dataframe
            Dataframe with list of locations. 
    """

    # Densitymaps for tests alltogether
    dens = go.Densitymap(lat=df.LAT, lon=df.LONG,
        radius=10,
        hoverinfo='skip', 
        showscale=False,
        showlegend=True,
        name="large number <br>of explosions",
        legend='legend2',
        colorscale=[[0, 'white'], [1, '#ffff00']]
    )
    fig.add_trace(dens)

    leg_dict = {
            'legend2' : {
            'yanchor' : "top",
            'y' : 0.21,
            'xanchor' : "left",
            'x' : 0.01,
            'font' : {'size' : 15},
            'orientation' : 'h',
            'bgcolor' : '#f9f9f9'
            }
        }

    fig.update_layout(
        leg_dict
    )


def draw_scatter(fig, df, mode="STATE", visible=True): 
    """Draw test density at location
    Parameters
    ---------
        fig : go.Figure
            Figure to draw the density plot on
        df : pd.Dataframe
            Dataframe with frequency list of locations
    """
    for i, s in enumerate(df[mode].unique()): 
        df_s = df[df[mode] == s]
        scatter = go.Scattermap(
            lon=df_s.LONG, lat=df_s.LAT, 
            below='',
            hovertemplate =
                '%{text}', text = [
                    f'''<b>{helpers.FIXEDLABELS_[state]}, N={count} </b> <br> Name(s): {name} <br> Yield(s): {kts} kt <br> Type(s): {expl_type} <br> Delivery: {expl_delivery} <br> Purpose(s): {purpose} <br> {time} ''' 
                    for (state, count, name, kts, time, expl_type, expl_delivery, purpose) 
                    in zip(df_s.STATE, df_s.COUNT, df_s.SHOTNAME, df_s.YIELD, df_s.YEAR, df_s.TYPE, df_s.DELIVERY, df_s.PUR)
                ],
            name =  s,
            marker = {'size' : 10},
            legend='legend1', 
            meta=mode, 
            visible=visible
            )

        fig.add_trace(scatter)

        if mode=="STATE":
            fig.update_traces(
                marker = {'size' : 10, "color" : helpers.COLORS_[s]}, 
                name = helpers.FIXEDLABELS_[s],
                selector={'name': s}) 

    leg_dict = {
            'legend1' : {
            'yanchor' : "top",
            'y' : 0.13, 
            'xanchor' : "left",
            'x' : 0.01, 
            'font' : {'size' : 15},
            'orientation' : 'h',
            'bgcolor' : '#f9f9f9'
            }
        }

    fig.update_layout(
        leg_dict
    )


def main(infilename, outfilename):
    """Main. 
    Parameters
    ---------
        infilename : str 
            filename of pickled pd.Dataframe with explosion locations
        outfilename : str
            filename for pickled go.Figure
    """

    df = helpers.load_pkl(infilename)
    
    dff = make_location_frequency_df(df)

    fig = go.Figure()

    draw_density(fig, df)
    draw_scatter(fig, dff)

    fig.update_layout(
        boxmode = 'group',
        map_style = 'open-street-map', 
        modebar_remove=['lasso'], 
        map_zoom = 0,
        margin={"r":0,"t":0,"l":0,"b":0},
        height=745, 
        width=16*55 # 16/em; 55em = fit for website
    )

    map_dict = {
            'bounds' : {
                    "north" : 85, 
                    "south" : -75, 
                    "east" : 180,
                    "west" : -179,
            },
            'center' : {
                    'lat' : 20, 
                    'lon' : 0 
            },
    }

    fig.update_maps(
            map_dict
    )

    if outfilename.find(".html") > -1:
        fig.write_html(outfilename)
    elif outfilename.find(".pkl") > -1:
        helpers.save_pkl(fig, outfilename)
    else: 
        print("[ERROR] You can save the figure only as .html or .pkl file. ")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--infilename", help="infilename", required=True)
    parser.add_argument("-o", "--outfilename", help="outfilename", required=True)

    args = parser.parse_args()

    main(args.infilename, args.outfilename)





