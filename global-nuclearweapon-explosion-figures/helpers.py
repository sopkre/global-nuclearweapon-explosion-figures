"""
Code snippet to jelp plotting, i/o and converting to strings.
"""

import pickle
import re
import numpy as np

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

PURPOSELABEL_ = {
"WR" : "weapons related",
"WR?" : "weapons related",
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
"WR/PR" : "weapons/peaceful research related",
None : "n/a",
"n/a" : "n/a",
"other" : "other"
} 

TYPESLABEL_ = {
    "A": "atmospheric",
    "AH": "high altitude", #"atmospheric (altitude 30-80 km)",
    "AW": "water surface", # "atmospheric, water surface",
    "AS": "surface", #"atmospheric, surface",
    "AX": "space", #(altitude > 80 km)",
    "UG": "underground", 
    "UW": "underwater",
    "CR": "cratering burst", #"cratering burst (shallow subsurface)"
}

DELIVERYLABEL_= {
        "AD": "airdrop",
        "B": "balloon",
        "R": "rocket or missile",
        "CM": "cruise missile",
        "BG": "barge",
        "AS": "anti-submarine weapon or torpedo",
        "T": "tower/tunnel",
        "T?": "tower/tunnel",
        "S":  "shaft",
        "S?" : "shaft",
        "TC":  "cavity in tunnel",
        "CS": "cavity, shaft",
        "M": "mine",
        None: "n/a",
        "n/a" : "n/a"
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
        s = "n/a"
    return s

YIELD_BINS_ = [0.01, 1, 10, 50, 100, 1000, 10000]


def format_yield_and_add_unit(bins=YIELD_BINS_):
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
    bins_s = format_yield_and_add_unit(bins)
    if (i == 0):
        s = f"< {bins_s[i]}"
    elif (i < len(bins)):
        s = f"{bins_s[i-1]} - {bins_s[i]}"
    else:
        s = f"> {bins_s[-1]}"
    if np.isnan(y): 
        s = "n/a"
    return s


def get_explosion_type(typestr): 
    """Get type (e.g. "underground") from explosion type (part before hyphen)
    Parameters
    ---------
        typestr : str
            TYPE string
    """
    return get_part_before_hyphen(typestr)


def get_delivery(typestr): 
    """Get delivery from explosion type (part after hyphen)
    Parameters
    ---------
        typestr : str
            TYPE string
    """
    return get_part_after_hyphen(typestr)

def get_explosion_purpose(p):
    """Formats explosion purpose (combine into "other" cat, remove "?")
    Parameters
    ---------
        p : str
            purpose string
    """
    p = get_part_before_hyphen(p)
    other = ["JV", "C", "WR/PR", "VU", "ST", "ME"]

    if type(p) is str:
        p = p.replace("?", "")

    if p is None or (type(p) is float and np.isnan(p)): 
        p = "n/a"

    if p in other:
        p = "other"

    return p


def make_yield_color_dict(bins=YIELD_BINS_):
    """Makes color dictionary for yield bins (increasingly darker red). 
    Parameters
    ---------
        bins : list of float 
            bins to convert to colour range
    """
    bins = format_yield_and_add_unit()
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