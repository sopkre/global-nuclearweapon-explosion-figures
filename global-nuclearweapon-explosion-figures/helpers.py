"""
Code snippet to jelp plotting, i/o and converting to strings.
"""

import pickle
import re

COLORS_ = {
    "FR" : '#e41a1c',
    "USSR" : '#377eb8',
    "DPRK" : '#4daf4a',
    "PAK" : '#984ea3',
    "PRC" : '#ff7f00',
    "IN" : '#a65628', 
    "US" : '#f781bf', 
    "UK" : '#999999', 
    "UNKNOWN" : 'black'}


FIXEDLABELS_ = {
    "DPRK" : "North Korea", 
    "FR" : "France", 
    "IN" : "India",
    "PAK" : "Pakistan",
    "PRC" : "China",
    "UK" : "UK",
    "UNKNOWN" : "Unknown*",
    "US" : "USA",
    "USSR" : "USSR/Russia",
    }

REGIONCOLORS_ = {
    'Northern America' : 'rgb(244,202,228)',
    'Central Asia' : 'rgb(253,205,172)', 
    'Northern Africa' : 'rgb(203,213,232)',  
    'Micronesia' : 'rgb(179,226,205)',
    'Eastern Europe' :  'rgb(230,245,201)',
    'Eastern Asia' : 'rgb(255,242,174)',  
    'Southern Asia' : 'rgb(241,226,204)',  
    'Australia and New Zealand' : 'rgb(204,204,204)',    
    'South Atlantic Ocean' : '#CAF0F8',
    'Arctic Ocean' : '#0077B6',
    'North Pacific Ocean' : '#00B4D8',
    'Indian Ocean' : '#90E0EF',
}

TYPECOLORS_ = {
    "A": "#ADB5BD",
    "AH": "#CED4DA",
    "AW": "#C2DFE3",
    "AS": "#6C757D",
    "AX": "#E9ECEF",
    "UG": "#212529", 
    "UW": '#90E0EF',
    "CR": "#343A40"
}

def add_breaks(s, f=2):
    """     
    Helper function to add line breaks (<br>) to long strings. 

    Parameters
    ----------
    s : str
        long expression
    f : int
        frequency of added breaks (e.g., f=2 means after every 2nd word)

    Returns
    ------
    Expression with breaks. 
    """
    listt = [m.start() for m in re.finditer(' ', s)]
    num = len(listt)
    output = ""
    if num < f:
        return s
    for i in range(0, num):
        if ((i-1)%f == 0):
            index = listt[i]
            output = s[:index] + '<br> ' + s[index+1:]
            s = output
            listt = [m.start() for m in re.finditer(' ', s)]
    return output.replace('<br> ', '<br>')


def make_range_string(ll):
    """     
    Takes list of numbers and makes string indicating range (e.g. [2, 45, 4] -> "2-45")
    Parameters
    ----------
    ll : list of floats
        list to convert to range string. 
    Returns
    -------
    String expression 
    """
    import numpy as np
    contains_nA = np.isnan(ll).any()
    ll = np.unique([x for x in ll if not np.isnan(x)])

    s = ""
    if len(ll) == 0:
        s = "n/A"
    if len(ll) == 1: 
        s = f"{ll[0]}" 
    if len(ll) > 1:
        s = f"{min(ll)}-{max(ll)}"

    if (contains_nA) and len(ll) > 0:
        s += " (+ n/A)"

    return s


def load_pkl(infilename): 
    """     
    Helper function to unpickle pkl file.

    Parameters
    ----------
    infilename : str
        input filename
    Returns
    ------
    unpickled file.  
    """
    pkl_file = open(f'{infilename}', 'rb')
    df = pickle.load(pkl_file)
    return df


def save_pkl(something, outfilename):
    """     
    Helper function to save something pkl file.

    Parameters
    ----------
    something : 
        something to pickle
    outfilename : str
        filename to save pkl to
    """
    output = open(outfilename, 'wb')
    pickle.dump(something, output)
    output.close()

def sort_list_by_score(ll, score):
    """Sorts list ll according to sorting of score list (i.e. ["x","c","d"] and [2,1,3] -> ["c","x","d"])
    ---------
        ll : list 
            list where order is changed according to sorted score
        score : list
            score list to sort list 
    """
    # Sort lists
    score, ll = zip(*sorted(zip(score, ll)))
    return ll[::-1]

def get_part_before_hyphen(s):
    """Deletes characters after (and including) hyphen
    ---------
        s : string 
            string to modify
    """
    if type(s) is str and s.find("-") > -1:
        s = s[:s.find("-")]
    return s

def get_part_after_hyphen(s):
    """Deletes characters after (and including) hyphen
    ---------
        s : string 
            string to modify
    """
    if type(s) is str and s.find("-") > -1:
        s = s[s.find("-")+1:]
    else: 
        s = None
    return s
