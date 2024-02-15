import sys
sys.path.append('../') 
from basic.basic import  createFolder
from plotting.plotRaster import plot_map
from plotting.plotVector import plot_mapVectorPolygons

def plotProjections(destName, city, cityDestPath, attr_value, scenario, year, districtPath, neighPath, streetsPath, waterPath, invertArea):
    srcPathTif = cityDestPath + '/data/GeoTIFF_AW/' + destName + '.tif'
    if scenario =='hist':
        exportPath =  cityDestPath + '/data/PNG_AW/{0}/'.format(attr_value, scenario)
    else:
        exportPath =  cityDestPath + '/data/PNG_AW/{0}/{1}/'.format(attr_value, scenario)
    createFolder(exportPath)
    title = 'Population: {0}, {1}, {2}'.format(attr_value, scenario, year)
    LegendTitle = 'Population'
    plot_map(city, 'popdistribution', srcPathTif, exportPath + destName + '.png' , title, LegendTitle, attr_value, districtPath, neighPath, streetsPath, waterPath, invertArea, addLabels=True)
        
        
def plotProjectionsVectors(destName, city, cityDestPath, attr_value, scenario, year, districtPath, neighPath, streetsPath, waterPath, invertArea):
    src_path = cityDestPath + '/data/GPKG/' + destName + '.geojson'
    if scenario =='hist':
        exportPath =  cityDestPath + '/data/PNG_vector/{0}/'.format(attr_value, scenario)
    else:
        exportPath =  cityDestPath + '/data/PNG_vector/{0}/{1}/'.format(attr_value, scenario)
    createFolder(exportPath)
    title = 'Population: {0}, {1}, {2}'.format(attr_value, scenario, year)
    LegendTitle = 'Population'
    #city, evalType, src, exportPath, title, LegendTitle, attr_value, districtPath, neighPath, waterPath, invertArea, streetsPath, addLabels=True
    plot_mapVectorPolygons(city, 'popdistribution', src_path, exportPath + destName + '.png' , title, LegendTitle, attr_value, districtPath, neighPath, streetsPath, waterPath, invertArea, addLabels=True)

def plotProjectionsVectorsAggr(destName, city, cityDestPath, attr_value, scenario, year, districtPath, neighPath, streetsPath, waterPath, invertArea):
    src_path = cityDestPath + '/data/censusTracts/' + destName + '_{0}.gpkg'.format(city)
    if scenario =='hist':
        exportPath =  cityDestPath + '/data/censusTracts/{0}/'.format(attr_value, scenario)
    else:
        exportPath =  cityDestPath + '/data/censusTracts/{0}/{1}/'.format(attr_value, scenario)
    createFolder(exportPath)
    title = 'Population: {0}, {1}, {2}'.format(attr_value, scenario, year)
    LegendTitle = 'Population'
    #city, evalType, src, exportPath, title, LegendTitle, attr_value, districtPath, neighPath, waterPath, invertArea, streetsPath, addLabels=True
    plot_mapVectorPolygons(city, 'popdistributionPolyg', src_path, exportPath + destName + '.png' , title, LegendTitle, attr_value, districtPath, neighPath, streetsPath, waterPath, invertArea, addLabels=True)