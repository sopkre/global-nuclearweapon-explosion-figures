# global-nuclearweapon-explosion-figures
Snippets to make interactive figures using data on global nuclear weapon explosions, e.g. maps. 

## Explosion location map 
```
plot_explosion_locations.py [-h] -i INFILENAME -o OUTFILENAME
```
where the infilename points to the pickled database of nuclear explosions, like from [here](https://github.com/sopkre/johnstonsarchive-nucleartest-reader/tree/main/obtained_data) and the outputfile where to save the pickled figure (or html-file if the extension is .html).

## Explosion numbers and totaled yield for world regions 
´´´
plot_region_piechart_map.py [-h] -i INFILENAME -o OUTFILENAME -t COORDINATELOOKUPTABLE -j COUNTRYREGIONJSON
´´´
where infilename and outfilename are the same as above; COORDINATELOOKUPTABLE points to a pickled dict that maps the explosion coordinates to states - if the file is not there, it will be created. If no state according to coordinate is found, the closest larger city is taken. COUNTRYREGIONJSON points to a json file mapping states to world region (according to UN geoscheme); if the file is not there, it will be downloaded from [here](https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/refs/heads/master/all/all.json).

## Height of burst 
```
plot_HOB.py [-h] -i INFILENAME -o OUTFILENAME
```
Arguments: See above.