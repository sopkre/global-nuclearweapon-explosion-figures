#!/usr/bin/env python3.13

"""
Snippet to make overview pie charts with basic info on nuclear weapon explosions 
(conducted state, region, type, purpose, and yield)

usage: plot_pies.py [-h] -i INFILENAME -o OUTFILENAME
"""

import argparse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import helpers

YIELD_BINS_ = [0.01, 1, 10, 50, 100, 1000, 10000]

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
        labels = [helpers.PURPOSELABEL_[x] if x not in ["other", "n/a"] else x for x in labels ]
        colors = px.colors.qualitative.Antique
    elif slice=="REGION": 
        colors = [helpers.REGIONCOLORS_[x] for x in labels]
    elif slice=="TYPE_SHORT": 
        colors = [helpers.TYPECOLORS_[x] for x in labels] 
        labels = [helpers.TYPESLABEL_[x] for x in labels]
    elif slice =="YIELD_CAT":
        color_dict = helpers.make_yield_color_dict()
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

    df["TYPE_SHORT"] = df["TYPE"].apply(lambda x: helpers.get_explosion_type(x))
    df["PUR_SHORT"] = df["PUR"].apply(lambda x: helpers.get_explosion_purpose(x))
    df["YIELD_CAT"] = df["YIELD"].apply(lambda x: helpers.get_yield_range_str(x, bins=YIELD_BINS_))

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




