#!/usr/bin/env python3.13

"""
Snippet to make overview pie charts with basic info on nuclear weapon explosions 
(conducted state, region, type, purpose, and yield)

usage: plot_pies.py [-h] -i INFILENAME -o OUTFILENAME
"""

import argparse
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import helpers

PURPOSELABEL_ = {
"WR" : "weapons related",
"FS" : "fundamental science",
"I" : "industrial applications",
    "I-CV" : "cavity excavation",
    "I-EM" : "earth-moving",
    "I-FE" : "extinguishing of oil/gas well fire",
    "I-OS" : "oil stimulation",
    "I-SS" : "seismic sounding",
"JV" : "joint verification",
"ME" : "military exercise",
"PR" : "research for peaceful applications",
"SE" : "safety experiment",
"ST" : "storage/transportation experiment",
"VU" : "Vela uniform",
"WE" : "weapons effects",
"C" : "combat use, strategic warfare", 
None : "NONE", 
"WR/P" : "WR/P"
} 

TYPES_ = {
    "A": "atmospheric",
    "AH": "high altitude", #"atmospheric (altitude 30-80 km)",
    "AW": "water surface", # "atmospheric, water surface",
    "AS": "surface", #"atmospheric, surface",
    "AX": "space", #(altitude > 80 km)",
    "UG": "underground", 
    "UW": "underwater",
    "CR": "cratering burst", #"cratering burst (shallow subsurface)"
}

DELIVERY_= {
        "AD": "airdrop",
        "B": "balloon",
        "R": "rocket or missile",
        "CM": "cruise missile",
        "BG": "barge",
        "AS": "anti-submarine weapon or torpedo",
        "T": "tower/tunnel",
        "S":  "shaft",
        "TC":  "cavity in tunnel",
        "CS": "cavity, shaft",
        "M": "mine"
}

YIELD_BINS_ = [0.01, 1, 10, 50, 100, 1000, 10000]

def get_explosion_type(typestr): 
    """Get type (e.g. "underground") from explosion type (part before hyphen)
    Parameters
    ---------
        typestr : str
            purpose string
    """
    return helpers.get_part_before_hyphen(typestr)

def get_delivery(typestr): 
    """Get delivery from explosion type (part after hyphen)
    Parameters
    ---------
        typestr : str
            purpose string
    """
    return helpers.get_part_after_hyphen(typestr)

def get_explosion_purpose(p):
    """Formats explosion purpose (combine into "other" cat, remove "?")
    Parameters
    ---------
        p : str
            purpose string
    """
    p = helpers.get_part_before_hyphen(p)
    other = ["JV", "C", "WR/PR", "VU", "ST", "ME"]

    if type(p) is str:
        p = p.replace("?", "")

    if p is None or (type(p) is float and np.isnan(p)): 
        p = "n/a"

    if p in other:
        p = "other"

    return p

def format_and_add_unit(bins=YIELD_BINS_):
    """Formats yield values (e.g. 1.0 -> 1) and adds units (e.g. kT, MT)
    Parameters
    ---------
        bins : list of float 
            bins to make formated list from
    """
    bins_s = []
    for b in bins:
        if b < 1:
            bins_s += [f"{b} kT"]
        elif b < 1000:
            bins_s += [f"{b:.0f} kT"]
        else:
            bins_s += [f"{b/1000:.0f} MT"]
    return bins_s

def get_yield_range_str(y, bins=YIELD_BINS_):
    """Formats bins to label list for yield ranges, e.g. ["< 0.1 kT", "0.1kT - 20 MT"] 
    Parameters
    ---------
        bins : list of float 
            bins to make formated list from
    """
    i = 0
    while i < len(bins) and y > bins[i]:
        i += 1  
    bins_s = format_and_add_unit(bins)
    if (i == 0):
        s = f"< {bins_s[i]}"
    elif (i < len(bins)):
        s = f"{bins_s[i-1]} - {bins_s[i]}"
    else:
        s = f"> {bins_s[-1]}"
    if np.isnan(y): 
        s = "n/a"
    return s

def make_yield_color_dict(bins=YIELD_BINS_):
    """Makes color dictionary for yield bins (increasingly darker red). 
    Parameters
    ---------
        bins : list of float 
            bins to convert to colour range
    """
    bins = format_and_add_unit()
    color_dict = {}

    for i in range(len(bins)+1):
        if (i == 0):
            key = f"< {bins[i]}"
        elif (i < len(bins)):
            key = f"{bins[i-1]} - {bins[i]}"
        else:
            key = f"> {bins[-1]}"
        color_dict[key] = f'rgb({(1-i/len(bins))*255}, 0, 0)'
    
    color_dict["n/a"] = 'rgb(240, 240, 240)'

    return color_dict




def make_pie(df, slice="STATE"):
    """Plot pie.
    Parameters
    ---------
        df : pd.Dataframe
            data to use
        slice : str 
            what dataframe column to use for pie chart 
    """
    values = []
    labels = df[slice].unique()

    values = [len(df[df[slice]==x]) for x in labels]
    sort = True

    import plotly.express as px
    colors = px.colors.qualitative.Pastel2

    if slice=="STATE":
        colors = [helpers.COLORS_[x] for x in labels]
        labels = [helpers.FIXEDLABELS_[x] for x in labels]
    elif slice=="PUR_SHORT": 
        labels = [PURPOSELABEL_[x] if x not in ["other", "n/a"] else x for x in labels ]
        colors = px.colors.qualitative.Antique
    elif slice=="REGION": 
        colors = [helpers.REGIONCOLORS_[x] for x in labels]
    elif slice=="TYPE_SHORT": 
        colors = [helpers.TYPECOLORS_[x] for x in labels] 
        labels = [TYPES_[x] for x in labels]
    elif slice =="YIELD_CAT":
        color_dict = make_yield_color_dict()
        labels = list(color_dict.keys())[::-1]
        values = [len(df[df[slice]==x]) for x in labels]
        colors = [color_dict[x] for x in labels]
        sort = False
    else: 
        pass

    t = go.Pie(
        values=values, 
        labels=labels, 
        direction='clockwise',
        sort=sort,
        textinfo='label', 
        name = '',
        hovertemplate='%{label} <br> N = %{value}',
        hole=.35,
        marker=dict(colors=colors, line=dict(width=1.5)),
        showlegend=False
        )
    return t


def set_layout(fig):
    """Sets layout of figure.
    Parameters
    ---------
        fig : go.Figure
            what figure layout should be applied to.
    """
    fig.update_layout(
        modebar_remove=['lasso'],     
        margin={"r":0,"t":0,"l":0,"b":0},
        height=800, 
        width=16*55, # 16/em; 55em = fit for website
    )


def main(infilename, outfilename):
    """Main. 
    Parameters
    ---------
        infilename : str 
            filename of pickled pd.Dataframe
        outfilename : str
            filename of pickled go.Figure or html
    """

    ### Prepare dataframe
    ### -----------------
    df = helpers.load_pkl(infilename)

    df["TYPE_SHORT"] = df["TYPE"].apply(lambda x: get_explosion_type(x))
    df["PUR_SHORT"] = df["PUR"].apply(lambda x: get_explosion_purpose(x))
    df["YIELD_CAT"] = df["YIELD"].apply(lambda x: get_yield_range_str(x))

    ### Make figure
    ### -----------

    fig = make_subplots(
        rows=2, 
        cols=6,
        specs=[
            [{"type": "domain", "colspan": 2}, None, {"type": "domain", "colspan": 2}, None, {"type": "domain", "colspan": 2}, None], 
            [None, {"type": "domain", "colspan": 2}, None, {"type": "domain", "colspan": 2}, None, None], 
            ],
        horizontal_spacing = 0.12, 
        vertical_spacing = 0.0
        )

    hole_text = [ ["Who?", None, "Where?", None, "How?", None], 
                  [None, "Why?", None, "How <br> big?", None, None] ]
    annot = []
    for i, row in enumerate(hole_text): 
        for j, t in enumerate(row): 
            if t is not None:
                annot += [ dict(text=f"{t}", x=sum(fig.get_subplot(i+1, j+1).x)/2, y=sum(fig.get_subplot(i+1, j+1).y)/2,
                        font_size=15, showarrow=False, xanchor="center", yanchor="middle") ]
    
    plot_vars = ["STATE", "REGION", "TYPE_SHORT", "PUR_SHORT", "YIELD_CAT"]
    pos = [(1,1), (1,3), (1,5), (2,2), (2,4)]

    for i, var in enumerate(plot_vars):
        t = make_pie(df, slice=var)
        fig.add_trace(t, row=pos[i][0], col=pos[i][1])

    fig.update_layout(annotations=annot)
    set_layout(fig)

    ### Save output
    ### -----------

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




