import geopandas as gpd, sys, os
import pandas as pd
import glob
import numpy as np
sys.path.append('./') 
from basic.basic import createFolder

import subprocess
from osgeo import gdal

def pointsTOgrid(gridPath, pointsPath, dst_path):
    """This function converts point dataset to grid cells 

    Args:
        gridPath (_str_): Path to folder where grid cell file is located.
        pointsPath (_str_): Path to folder where input GPKG is located.
        dst_path (_str_): String for destination file name of grids in gpkg.
    """    
    try: 
        os.path.exists(gridPath) == True
        os.path.exists(pointsPath) == True
    except:
        print("Input is not defined")
    else:
        polys = gpd.read_file(gridPath, crs="EPSG:3035")
        gdf_points= gpd.read_file(pointsPath, crs="EPSG:3035")
        if 'FID' not in polys.columns:
            if 'fid' in polys.columns:
                polys = polys.rename(columns={'fid':'FID'})
            else: polys['FID'] = np.arange(len(polys))
        
        gdf_joined = gpd.sjoin(gdf_points, polys, how='left', op='within') # Here I am using intersects with left join
        #remove the point geometry and add the polygon geometry
        gdf = gdf_joined.loc[:, gdf_joined.columns != 'geometry']
        gdf_merged = gdf.merge(polys, how='inner', on='FID')
        gdf_merged['FID'] = gdf_merged['FID'].astype(int) # = gdf_merged.drop(columns=['FID'])
        gdf_merged.to_file(dst_path, driver='GeoJSON', crs='EPSG:3035')
    
def combineGeoJSON(geojsonPath, dst_csv, dst_vector, destNameWhole, attr_values,city):
    """This function combined individual GPKG files into one and produces the corresponding csv file.
    Args:
        geojsonPath (_str_): Path to folder where input GPKG are located.
        dst_csv (_str_): String for destination file name of points in csv.
        dst_vector (_str_): String for destination file name of points in gpkg.
        destNameWhole (_str_): String of file name where year and/or scenario are included.
        attr_values (_list_): List of migrant groups.
    """    
    files = glob.glob(geojsonPath + '/{0}_*.geojson'.format(destNameWhole))
    if city =='cph': natives='DNK'       
    elif city =='grootams' or city =='ams': natives='NLD'     
    elif city =='crc' : natives='POL'      
    elif city =='rom' : natives='ITA'
            
    if len(attr_values) == len(files):
        
        appended_data =[]
        for i in files:
            name = i.split('{0}_'.format(destNameWhole))[-1].split('.geojson')[0]
            if name!= natives:
                df = gpd.read_file(i)
                #df = df.drop(columns=['lat','lon','geometry'])
            else: df = gpd.read_file(i)

            df['id'] = np.arange(len(df))        
            df = df.loc[df['{}'.format(name)] > 0 ]
            df = df.set_index('id')
            appended_data.append(df)
        
        lf = pd.DataFrame()
        for df in appended_data:
            if lf.empty:
                # if the merged dataframe is empty, assign the first dataframe to it
                lf = df
            else:
                # if the merged dataframe is not empty, merge the current dataframe with it
                lf= pd.merge(lf, df, on='geometry')

        #lf = pd.concat(appended_data, axis=1)
        for i in lf.columns:
            if i not in ['geometry','lat','lon']:
                lf[i] = lf[i].fillna(0)
        
        if city =='cph':
            lf['totalmig']= lf['EU_West']+ lf['EU_East']+ lf['EurNonEU']+ lf['MENAP']+ lf['Turkey']+ lf['OthNonWest']+ lf['OthWestern']
            lf['totalpop']= lf['totalmig'] + lf['DNK']
        elif city =='grootams' or city =='ams':
            lf['totalmig']= lf['EU West']+ lf['EU East']+ lf['Other Europe etc']+ lf['Turkey + Morocco']+ lf['Middle East + Africa']+ lf['Former Colonies']
            lf['totalpop']= lf['totalmig'] + lf['NLD']
        elif city =='crc' : 
            lf['totalmig']= lf['EuropeEU']+ lf['EurNonEU']+ lf['Other']
            lf['totalpop']= lf['totalmig'] + lf['POL']
        elif city =='rom' : 
            lf['totalmig']= lf['BGD']+ lf['PHL']+ lf['ROU']+ lf['EU']+ lf['nonEUEu']+ lf['Africa'] + lf['America']+ lf['Asia']
            lf['totalpop']= lf['totalmig'] + lf['ITA']
        
        lf['eurogrid']= lf['lon'].astype(int).astype(str) + 'N' + lf['lat'].astype(int).astype(str) + 'E'

        print(lf.head(2), lf.columns)
        lf = lf.drop(columns=['lat_x','lon_x', 'lat_y', 'lon_y'])
        #WRITE DATAFRAME TO CSV
        lf.to_csv(dst_csv)
        
        ldf = gpd.GeoDataFrame(lf, geometry='geometry', crs='EPSG:3035')
        ldf.to_file(dst_vector, driver='GeoJSON')
    else: 
        print("Input is not correct")
    
    
def rastertoshp(python_scripts_folder_path, src_file, dst_file, attr_value):#src_file, dst_file, polyPath):
    cmds = """python {0}/gdal_polygonize.py "{1}"  -f "GeoJSON" "{2}" "{3}" """.format(python_scripts_folder_path, src_file, dst_file, attr_value)
    print(cmds)
    subprocess.call(cmds, shell=True)
    #zonalStat(src_file, dst_file, polyPath, 'sum')
    
    
import geopandas as gpd
import json
from rasterstats import zonal_stats
# Calculate zonal statistics from tiffs
def zonalStat(src_file, dst_file, polyPath, statistics):  
    # Read Files
    districts = gpd.read_file(polyPath)
    districts = districts.to_crs("EPSG:3035")
    
    zs = zonal_stats(districts, src_file,
                stats='{}'.format(statistics), all_touched = False, percent_cover_selection=None, percent_cover_weighting=False, #0.5-->dubled the population
                percent_cover_scale=None,geojson_out=True)
    
    for row in zs:
        newDict = row['properties']
        for i in newDict.keys():
            if i == '{}'.format(statistics):
                newDict['{}_'.format(statistics)] = newDict.pop(i)
        
    result = {"type": "FeatureCollection", "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::3035" } }, "features": zs}
    #dst_file = dstPath + "{0}".format(dstFile) #
    with open(dst_file , 'w') as outfile:
        json.dump(result, outfile)
    
def shptoraster(raster_file, src_file, gdal_rasterize_path, dst_file, column_name, xres=100, yres=100):
    '''
    Takes the path of GeoDataframe and converts it to raster
        raster_file         : str
            path to base raster, from which the extent of the new raster is calculated 
        src_file            : str
            path to source file (SHP,GEOJSON, GPKG) 
        gdal_rasterize_path : str
            path to execute gdal_rasterize.exe
        dst_file            : str
            path and name of the destination file
        column_name         : str
            Field to use for rasterizing
    '''
    data = gdal.Open(raster_file)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None    
    cmd = '{0}/gdal_rasterize.exe -a "{9}" -te {1} {2} {3} {4} -tr {5} "{6}" "{7}" "{8}"'\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
                
    subprocess.call(cmd, shell=True)
    
def rasterizeFiles(year, src_filePath, raster_file, gdal_rasterize_path):
    src_file = src_filePath + "/data/GPKG/{0}.geojson".format(year)
    gdf = gpd.read_file(src_file)
    print(gdf.head(3))
    createFolder(src_filePath + "/data/GeoTIFF/")
    for i in gdf.columns: 
        if i != 'geometry' and i != 'grid_geometry_epsg3035' and i != 'lat' and i != 'lon':
            dst_file = src_filePath + "/data/GeoTIFF/{0}_{1}.tif".format(year, i)
            shptoraster(raster_file, src_file, gdal_rasterize_path, dst_file, i, xres=100, yres=100) 
            
def gpkgTOcsv(src_file, dst_file):
    if os.path.isfile(src_file) == True:
        gdf = gpd.read_file(src_file, driver='GeoJSON', crs='EPSG:3035')
        if 'lat' and 'lon' in gdf.columns:
            for i in gdf.columns:
                if i != 'geometry':
                    gdf['{}'.format(i)] = gdf['{}'.format(i)].fillna(0)
            gdf['totalpop'] = gdf['totalmig'] + gdf['POL']
            gdf.to_file(src_file, driver='GeoJSON',crs="EPSG:3035")
            gdf.to_csv(dst_file, sep=',')
        else:
            gdf['Center_point'] = gdf['geometry'].centroid
            #Extract lat and lon from the centerpoint
            gdf["lat"] = gdf.Center_point.map(lambda p: p.x)
            gdf["lon"] = gdf.Center_point.map(lambda p: p.y)
            gdf = gdf.drop(columns={'Center_point', 'geometry'})
            gdf.to_csv(dst_file, sep=',')
    else: print('NO INPUT')
    
import rasterio  
def writeRaster(raster_file, outfile, out_array):
    with rasterio.open(raster_file) as src:
        new_dataset = rasterio.open(
            outfile,
            'w',
            driver='GTiff',
            height=src.shape[0],
            width=src.shape[1],
            count=1,
            dtype=out_array.dtype,
            crs=src.crs,
            transform= src.transform
            )
    new_dataset.write(out_array, 1)
    new_dataset.close()