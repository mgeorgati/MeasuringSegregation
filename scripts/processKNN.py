import os 
import glob
from basic.basic import createFolder
from basic.rasterToshp import mainRaster
from calcKNN.plot_KNN import plot_KNNneigh
from calcKNN.estimateSumKNN import estimateKNN, calc_summaryKNN_sums
from config.config import python_scripts_folder_path
from calcKNN.combineCSV_knn import combineGeoJSON
from config.config import gdal_rasterize_path

def process_KNN(city, scenario, attr_value, year, srcNameDef,
                        calc_KNNneigh, templatePath, yearPrevious, calc_Conv, plot_knn, plot_knn_dif, 
                        estimate_sum_knn, init_raster_shp): 
    
    if city == 'ams':
        from config.ams import (cityDestPath, districtPath, invertArea, raster_file,
                                neighPath, srcPath, streetsPath, waterPath)
        
    elif city == 'cph':
        from config.cph import (cityDestPath, districtPath, invertArea,raster_file,
                                neighPath, srcPath, streetsPath, waterPath)
        
    elif city == 'crc':
        from config.crc import (cityDestPath, districtPath, invertArea,raster_file,
                                neighPath, srcPath, streetsPath, waterPath)
        
    elif city == 'rom':
        from config.rom import (cityDestPath, districtPath, invertArea,raster_file,
                                neighPath, srcPath, streetsPath, waterPath)
    
    if year <= 2021 :
        destName = '{1}_{2}'.format(scenario, year, attr_value)
        destNameWhole = '{1}'.format(scenario, year, attr_value)
    else:
        destName = '{1}_{0}_{2}'.format(scenario, year, attr_value)
        destNameWhole = '{1}_{0}'.format(scenario, year, attr_value)
        

    if calc_KNNneigh == "yes":
        if attr_value == 'totalpop':
            nnn = 200
        else: nnn = 50
        plot_KNNneigh(city, scenario, attr_value, nnn, cityDestPath, destName, waterPath, templatePath, yearPrevious,
                  year, districtPath, neighPath, streetsPath, waterPath,
                  calc_Conv, plot_knn, plot_knn_dif, estimate_sum_knn)
    # Estimate total sums of neighbours
    if estimate_sum_knn =="yes" :
        inputPath = cityDestPath + "/data/GeoTIFF/{0}.tif".format(destName)
        estimateKNN(inputPath, raster_file, templatePath, cityDestPath, destName)

    if init_raster_shp == "yes":
        for i in range(5):
            src_file = cityDestPath + "/data/KNN/SUMs/conv_sum_{1}_{0}.tif".format(destName,i)
            createFolder(cityDestPath + "data/KNN/GeoJSON")
            outSHPfn = cityDestPath + "data/KNN/GeoJSON/conv_sum_{1}_{0}.geojson".format(destName,i)
            
            print('| Converting raster to vector layer')
            mainRaster(src_file, outSHPfn, attr_value)

def process_KNN_total(city,scenario, attr_values, year, init_shp_gpkg, removeFilles):
    if city == 'grootams':
        from config.grootams import cityDestPath, gridPath
        streetsPath= None 
    elif city == 'ams':
        from config.ams import cityDestPath, gridPath
    elif city == 'cph':
        from config.cph import cityDestPath, gridPath
    elif city == 'crc':
        from config.crc import cityDestPath, gridPath
    elif city == 'rom':
        from config.rom import cityDestPath, gridPath
    
    if year<=2021 :
        destNameWhole = '{0}'.format(year,)
    else:
        destNameWhole = '{1}_{0}'.format(scenario, year)

    if init_shp_gpkg == "yes":
        for i in range(5):
            geojsonPath = cityDestPath + "data/KNN/GeoJSON/"
            dst_vector = cityDestPath + "data/KNN/GPKG/{0}_{1}_points.geojson".format(destNameWhole,i)
            
            if i == 4: dst_csv = cityDestPath + "data/KNN/CSV/{0}_neigh.csv".format(destNameWhole, i)
            else: dst_csv = cityDestPath + "data/KNN/CSV/{0}_{1}.csv".format(destNameWhole, i)
            
            orig_csv = cityDestPath + "data/KNN/CSV/{0}_{1}.csv".format(destNameWhole, i-1)
            if not os.path.exists(orig_csv): orig_csv = cityDestPath + "data/CSV/{0}.csv".format(destNameWhole)
            createFolder(cityDestPath + "data/KNN/GPKG/")
            createFolder(cityDestPath + "data/KNN/CSV/")
            
            print('| Combining the individual countries to one GPKG ans CSV file')
            combineGeoJSON(geojsonPath, dst_csv, dst_vector, destNameWhole,orig_csv, attr_values, city,scenario, i)
    
        if removeFilles == "yes":
            for hgx in glob.glob(geojsonPath + '/conv_sum_{0}_*.geojson'.format(i, destNameWhole)):
                os.remove(hgx)
            for hgx in glob.glob(cityDestPath + 'data/KNN/SUMs/conv_sum_{0}_*.tif'.format(i, destNameWhole)):
                os.remove(hgx)
    
    