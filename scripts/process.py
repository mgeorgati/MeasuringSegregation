import os 
from basic.basic import createFolder
from basic.moveNega import fixNegatives, removeRandomPeople
from basic.summaryStat import summaryStatistics
from basic.calcDissimilarity import calcDissimilarity
from basic.conversions import combineGeoJSON, pointsTOgrid, rastertoshp
from basic.fixStructure import processProjections, calcDifference
from basic.rasterToshp import mainRaster
from calcKNN.plot_KNN import plot_KNNneigh
from config.config import python_scripts_folder_path
from plotting.createGifs import createGIFs
from plotting.plot import plotProjections, plotProjectionsVectors


def process_Projections(city, scenario, attr_value, year, srcNameDef,
                        processRawOutput, init_calc_dif, fix_negative_values,
                        init_raster_shp, 
                        
                        plotMaps100, 
                        calc_KNNneigh, templatePath, yearPrevious, calc_Conv, plot_knn, plot_knn_dif): 
    
    if city == 'grootams':
        from config.grootams import (cityDestPath, districtPath, invertArea,
                                     neighPath, srcPath, streetsPath, 
                                     waterPath)
     
    elif city == 'ams':
        from config.ams import (cityDestPath, districtPath, invertArea,
                                neighPath, srcPath, streetsPath, waterPath)
        
    elif city == 'cph':
        from config.cph import (cityDestPath, districtPath, invertArea,
                                neighPath, srcPath, streetsPath, waterPath)
        
    elif city == 'crc':
        from config.crc import (cityDestPath, districtPath, invertArea,
                                neighPath, srcPath, streetsPath, waterPath)
        
    elif city == 'rom':
        from config.rom import (cityDestPath, districtPath, invertArea,
                                neighPath, srcPath, streetsPath, waterPath)
    
    if year <= 2021 :
        destName = '{1}_{2}'.format(scenario, year, attr_value)
        destNameWhole = '{1}'.format(scenario, year, attr_value)
    else:
        destName = '{1}_{0}_{2}'.format(scenario, year, attr_value)
        destNameWhole = '{1}_{0}'.format(scenario, year, attr_value)
        if year == 2030:
            destName_previous = '2020_{2}'.format(scenario, year, attr_value)
        else:
            yearPrevious = year - 10
            destName_previous = '{1}_{0}_{2}'.format(scenario, yearPrevious, attr_value)
    createFolder(cityDestPath + "data/GeoTIFF")
    if processRawOutput == 'yes':
        # Check how many files exist if exist in scrFolder
        # Copy + remane tifs from Spatial Disaggregation folder to MeasuringSegreagation folder,
        # newName = scenario + year + attr   
        processProjections(city, scenario, attr_value, year, srcNameDef, srcPath, cityDestPath)
    
    if init_calc_dif == "yes":
        if year == 2030:
            src_file_previous = cityDestPath + "data/GeoTIFF/{0}.tif".format(destName_previous)
        else:
            src_file_previous = cityDestPath + "data/GeoTIFF_sum/{0}.tif".format(destName_previous)
        src_file = cityDestPath + "data/GeoTIFF_dif/{0}.tif".format(destName)
        print(src_file, src_file_previous)
        createFolder(cityDestPath + "data/GeoTIFF_sum")
        dest_path = cityDestPath + "data/GeoTIFF_sum/{0}.tif".format(destName)
        
        print('| Converting raster to vector layer')
        calcDifference( src_file, src_file_previous, dest_path)
        print('------------------------------ Converting raster to vector layer was succesfull ------------------------------')
        print('------------------------------ for {0}, in {1}, in scenario:{2}, in year:{3} ------------------------------'.format(attr_value, city, scenario, year))
    
    if fix_negative_values == "yes":
        print(year, scenario, attr_value)
        
        src_path = cityDestPath + "data/GeoTIFF_sum/{0}.tif".format(destName)
        src_file_previous = cityDestPath + "data/GeoTIFF/2020_{0}.tif".format(attr_value)
        fraster = cityDestPath + "data/GeoTIFF/{0}.tif".format(destName)
        
        removeRandomPeople(src_path, src_file_previous, fraster)
        # This is an alternative , where the negative values are added on the nearest cell with value>abs(neg)
        #pointsPath = cityDestPath + "data/SHP/{0}.geojson".format(destName)
        #dst_path = cityDestPath + "data/SHP/{0}_fixed.geojson".format(destName)
        #fixNegatives(pointsPath, attr_value, dst_path)

    if init_raster_shp == "yes":
        src_file = cityDestPath + "data/GeoTIFF/{0}.tif".format(destName)
        createFolder(cityDestPath + "data/SHP")
        outSHPfn = cityDestPath + "data/SHP/{0}.geojson".format(destName)
        
        print('| Converting raster to vector layer')
        mainRaster(src_file,outSHPfn, attr_value)
        print('------------------------------ Converting raster to vector layer was succesfull ------------------------------')
        print('------------------------------ for {0}, in {1}, in scenario:{2}, in year:{3} ------------------------------'.format(attr_value, city, scenario, year))
    
    

    if plotMaps100 == 'yes':
        plotProjections(destName, city, cityDestPath, attr_value, scenario, year, districtPath, neighPath, streetsPath, waterPath, invertArea)
        #plotProjectionsVectors(destNameWhole , city, cityDestPath, attr_value, scenario, year, districtPath, neighPath, streetsPath, waterPath, invertArea)

    if calc_KNNneigh == "yes":
        if attr_value == 'totalpop':
            nnn = 200
        else: nnn = 25
        plot_KNNneigh(city, scenario, attr_value, nnn, cityDestPath, destName, waterPath, templatePath, yearPrevious,
                  year, districtPath, neighPath, streetsPath, waterPath,
                  calc_Conv, plot_knn, plot_knn_dif)
                
def process_ProjectionsTotal(city, scenario, attr_values, year,
                        init_shp_gpkg, init_point_cell, 
                        init_calc_summary, init_calc_dis,
                        
                        ): 
    
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
    
    if year<=2020 :
        destNameWhole = '{0}'.format(year,)
    else:
        destNameWhole = '{1}_{0}'.format(scenario, year)
    
    createFolder(cityDestPath + "Indexes")
    if init_shp_gpkg == "yes":
        geojsonPath = cityDestPath + "data/SHP/"
        dst_vector = cityDestPath + "data/GPKG/{0}_points.geojson".format(destNameWhole)
        dst_csv = cityDestPath + "data/CSV/{0}.csv".format(destNameWhole)
        
        createFolder(cityDestPath + "data/GPKG/")
        createFolder(cityDestPath + "data/CSV/")
        
        print('| Combining the individual countries to one GPKG ans CSV file')
        combineGeoJSON(geojsonPath, dst_csv, dst_vector, destNameWhole, attr_values,city)
        print('------------------------------ Combining the individual countries to one GPKG and CSV file was succesfull ------------------------------')
        print('------------------------------ for {0}, in scenario:{1}, in year:{2} ------------------------------'.format(city, scenario, year))
    
    if init_point_cell == "yes":
        # Convert points to gridCells
        dst_vector = cityDestPath + "data/GPKG/{0}_points.geojson".format(destNameWhole)
        dst_path = cityDestPath + "data/GPKG/{0}.geojson".format(destNameWhole)
        
        print('| Converting the point dataset to grid cells GPKG')
        pointsTOgrid(gridPath, dst_vector, dst_path)
        print('------------------------------ Converting the point dataset to grid cells GPKG file was succesfull ------------------------------')
        print('------------------------------ for {0}, in scenario:{1}, in year:{2} ------------------------------'.format(city, scenario, year))

    if init_calc_summary == "yes":
        # Convert points to gridCells
        src_path = cityDestPath + "data/GPKG/{0}.gpkg".format(destNameWhole)
        if not os.path.exists(src_path): src_path = cityDestPath + "data/GPKG/{0}.geojson".format(destNameWhole)
            
        dst_path = cityDestPath + "Indexes/summaryCells_{}.xlsx".format(scenario)
        print('| ')
        summaryStatistics(src_path, dst_path, attr_values, city, scenario, year)
        print('------------------------------  ------------------------------')
        print('------------------------------ for {0}, in scenario:{1}, in year:{2} ------------------------------'.format(city, scenario, year))

    if init_calc_dis == "yes":
        srcPath = cityDestPath + "data/GPKG/{0}.geojson".format(destNameWhole)
        dissimFile = cityDestPath + "Indexes/dissimilarity_{}.csv".format(scenario)
        
        
        print('| Estmating the dissimilarity index')
        calcDissimilarity(srcPath, dissimFile, year, attr_values, city)
        print('------------------------------ Estmating the dissimilarity index was succesfull ------------------------------')
        print('------------------------------ for {0}, in scenario:{1}, in year:{2} ------------------------------'.format(city, scenario, year))
        
def process_ProjectionsNoYear(city, attr_values, scenario, create_GIFs):
    
    if city == 'grootams':
        from config.grootams import cityDestPath
    elif city == 'ams':
        from config.ams import cityDestPath
    elif city == 'cph':
        from config.cph import cityDestPath
    elif city == 'crc':
        from config.crc import cityDestPath 
    elif city == 'rom':
        from config.rom import cityDestPath
        
    if create_GIFs == "yes":
        export_path = cityDestPath + "/data/GIFs/"
        createFolder(export_path)

        for i in attr_values: 
            if scenario == 'hist':
                src_path = cityDestPath + "/data/PNG/{}/".format(i)
            else:
                src_path = cityDestPath + "/data/PNG/{0}/{1}".format(i, scenario)
            createGIFs(src_path, export_path, i + '_' + scenario)
        
    
    
    
    
    