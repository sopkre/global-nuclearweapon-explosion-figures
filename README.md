# global-nuclearweapon-explosion-figures
Snippets to make interactive figures using data on global nuclear weapon explosions, e.g. maps. 

## Explosion location map 
```
plot_explosion_locations.py [-h] -i INFILENAME -o OUTFILENAME
```
where the infilename points to the pickled database of nuclear explosions, like from [here](https://github.com/sopkre/johnstonsarchive-nucleartest-reader/tree/main/obtained_data) and the outputfile where to save the pickled figure (or html-file if the extension is .html).

## Height of burst 
```
plot_HOB.py [-h] -i INFILENAME -o OUTFILENAME
```
Arguments: See above.