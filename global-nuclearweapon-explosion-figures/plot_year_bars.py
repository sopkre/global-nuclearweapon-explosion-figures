#!/usr/bin/env python3.13

"""
Snippet to plot histograms of nuclear explosion numbers over years. 

Usage: plot_year_bars.py [-h] -i INFILENAME -o OUTFILENAME
"""

import argparse
import plotly.graph_objects as go
import plotly.express as px

import helpers

YIELD_BINS_ = [0.01, 1, 10, 50, 100, 1000, 10000]

CATEGORY_DICT_= {
    "STATE" : "State", 
    "REGION" : "Region", 
    "TYPE_SHORT" : "Type", 
    "PUR_SHORT" : "Purpose", 
    "YIELD_CAT" : "Yield", 
    "DELIVERY" : "Method"}

def make_year_histogram(df, category="STATE", value="US", name=None, color=None, visible=True):
    """Plot histograms of nuclear explosion numbers per year.
    Parameters
    ---------
        df : pd.Dataframe
            data to use
        category : str
            category for colors (i.e. STATE to color according to state)
        value : str
            value for category (i.e. "US" for category "STATE")
        name : str
            name of trace, for legend and hoverlabel
        color : str
            fill color of histogram 
        visible : bool
            whether trace is visible at beginning (changed with buttons)
    """

    if name is None:
        name=value

    df = df[df[category]==value]

    t = go.Histogram(x=df.YEAR, 
        name=name, 
        marker={"color": color, "line": {"width":1.5}}, 
        hovertemplate = '<b>%{x}</b> <br>N = %{y}', 
        legend = "legend1",
        xaxis="x1", 
        yaxis="y1",
        visible=visible,
        meta=category
    )
    return t


def set_layout(fig):
    """Set layout of figure. 
    Parameters
    ---------
        fig : go.Figure
            figure to apply layout to
    """
    fig.update_layout(
        modebar_remove=['lasso', 'select'], 
        barmode='stack',
        xaxis1=dict(
            title=dict(text="Year")),
        yaxis1=dict(
            title=dict(text="Number of nuclear weapon explosions"),
            ),        
        margin={"r":0,"t":0,"l":0,"b":0},
        height=800, 
        width=16*55, # 16/em; 55em = fit for website
        legend1 = {
            'yanchor' : "top",
            'y' : 0.98, 
            'xanchor' : "right",
            'x' : 0.98, 
            'font' : {'size' : 15}}
        )


def add_buttons(fig, mode_label_dict):
    """Add the buttons to switch between modes
    ---------
        fig : go.Figure
            figure to add legend to
        mode_label_dict : dict
            keys: mode to add (e.g. "STATE"), values: title for respecive button
    """

    other_traces = [not isinstance(f, go.Histogram) for f in fig.data ]

    traces = []
    modes = []
    for mode in mode_label_dict:
        traces += [ [f.meta==mode for f in fig.data] ]
        modes += [mode]

    buttons = []
    for i, t in enumerate(traces):
        buttons += [dict(label=mode_label_dict[modes[i]],
            method="update",
            args=[{"visible": [ x | y for (x,y) in zip(other_traces, t)] }] 
            )]

    menu_dict = {'updatemenus' : [
        dict(
            type="buttons",
            direction="right",
            active=0,
            x=0.00,
            y=1.03,
            xanchor='left', 
            yanchor='bottom', 
            buttons=buttons,
            font_size=15
        )
    ]}

    fig.update_layout(
        menu_dict
    )


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
    df["TYPE_SHORT"] = df["TYPE"].apply(lambda x: helpers.get_explosion_type(x))
    df["PUR_SHORT"] = df["PUR"].apply(lambda x: helpers.get_explosion_purpose(x))
    df["YIELD_CAT"] = df["YIELD"].apply(lambda x: helpers.get_yield_range_str(x, YIELD_BINS_))
    df["DELIVERY"] = df["TYPE"].apply(lambda x: helpers.get_delivery(x))

    fig = go.Figure()
    
    # State #
    #--------
    for s in df.STATE.unique():
        t = make_year_histogram(df, category="STATE", value=s, color=helpers.COLORS_[s], name=helpers.FIXEDLABELS_[s])
        fig.add_trace(t) 

    # Region #
    #--------
    for i, r in enumerate(df.REGION.unique()):
        t = make_year_histogram(df, category="REGION", value=r, visible=False, color=helpers.REGIONCOLORS_[r])
        fig.add_trace(t) 

    # Type #
    #--------
    for i, r in enumerate(df.TYPE_SHORT.unique()):
        t = make_year_histogram(df, category="TYPE_SHORT", value=r, visible=False, color=helpers.TYPECOLORS_[r], name=helpers.TYPESLABEL_[r])
        fig.add_trace(t) 
    
    # Purpose #
    #----------
    for i, r in enumerate(df.PUR_SHORT.unique()):
        t = make_year_histogram(df, category="PUR_SHORT", value=r, visible=False, name=helpers.PURPOSELABEL_[r], color=px.colors.qualitative.Antique[i])
        fig.add_trace(t) 
    
    # Yield categories #
    #-------------------
    color_dict = helpers.make_yield_color_dict()
    for i, r in enumerate( list(color_dict.keys()) ):
        t = make_year_histogram(df, category="YIELD_CAT", value=r, visible=False, color=color_dict[r])
        fig.add_trace(t) 
    
    # Method #
    #---------
    for i, r in enumerate( sorted(df.DELIVERY.unique())):
        t = make_year_histogram(df, category="DELIVERY", value=r, visible=False, name=helpers.DELIVERYLABEL_[r], color=helpers.DELIVERYCOLOR_[r])
        fig.add_trace(t) 
    
    add_buttons(fig, 
        CATEGORY_DICT_
    )

    set_layout(fig)

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




