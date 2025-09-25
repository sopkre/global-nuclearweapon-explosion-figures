#!/usr/bin/env python3.13

"""
Snippet to plot height of burst values over years. 

Usage: plot_HOB.py [-h] -i INFILENAME -o OUTFILENAME
"""

import argparse
import numpy as np
import plotly.graph_objects as go

import helpers

def plot_HOB(fig, df):
    """Makes HOB plot. 
    Parameters
    ---------
        fig : go.Figre 
            figure to plot HOBs on
        df : pd.Dataframe
            data to use
    """
    
    for i, s in enumerate(np.unique(df.STATE)[::-1]): 
        df_s = df[df.STATE == s]
        df_s = df_s[df_s.DATETIME.notna()]

        scatter = go.Scatter(x=df_s.DATETIME, y=df_s.HOB, 
        name = helpers.FIXEDLABELS_[s], 
        mode = "markers",
        hovertemplate =
                '%{text}', text = [
                    f'''<b>{helpers.FIXEDLABELS_[state]}, </b> <br> Name(s): {name} <br> Height: {hob}m <br> {time:%Y-%m-%d %H:%M}''' 
                    for (state, name, hob, time) 
                    in zip(df_s.STATE, df_s.SHOTNAME, df_s.HOB, df_s.DATETIME)
                ],
        legend='legend1', 
        marker = {"color" : helpers.COLORS_[s]}, 
        )

        fig.add_trace(scatter)

    fig.add_annotation(
            ax=1952, x=1954, 
            ay=3500, y=4900,
            text="Some more <br> at > 8000m",
            showarrow=True,
            arrowhead=1, 
            axref="x", ayref="y")


def main(infilename, outfilename):
    """Main. 
    Parameters
    ---------
        infilename : str 
            filename of pickled pd.Dataframe
        outfilename : str
            filename of pickled go.Figure
    """
    
    df = helpers.load_pkl(infilename)

    fig = go.Figure()  

    plot_HOB(fig, df)

    fig.update_layout(
        modebar_remove=['lasso'], 
        map_zoom = 0,
        xaxis=dict(
            title=dict(text="Year")),
        yaxis=dict(
            range=[-3200, 5000],
            title=dict(text="Height of burst [m]"),
            ),        
        margin={"r":0,"t":0,"l":0,"b":0},
        height=500, 
        width=16*55, # 16/em; 55em = fit for website
        legend1 = {
            'yanchor' : "top",
            'y' : 0.95, 
            'xanchor' : "left",
            'x' : 0.8, 
            'font' : {'size' : 15},
        }
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




