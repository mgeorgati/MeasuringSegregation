import sys
sys.path.append('./') 
from basic.basic import createFolder
from calcKNN.calc_KNN import calcConv, plotKNN, plotKNN_dif

def plot_KNNneigh(city, scenario, attr_value, nnn, cityDestPath, destName, raster_file, templatePath, yearPrevious,
                  year, districtPath, neighPath, streetsPath, waterPath,
                  calc_Conv, plot_knn, plot_knn_dif,
                  estimate_sum_knn):
    
    createFolder(cityDestPath + "/data/KNN/GeoTIFF")
    createFolder(cityDestPath + "/data/KNN/PNG")
    createFolder(cityDestPath + "/data/KNN/SUMs")
    if calc_Conv == 'yes':
        inputPath = cityDestPath + "/data/GeoTIFF/{0}.tif".format(destName)
        outPath = cityDestPath + "/data/KNN/GeoTIFF/conv_{0}_{1}.tif".format(destName,nnn)
        calcConv(inputPath, raster_file, nnn, outPath, templatePath)
    
    if plot_knn == 'yes':
        inputPath = cityDestPath + "/data/KNN/GeoTIFF/conv_{0}.tif".format(destName)
        exportPath = cityDestPath + "/data/KNN/PNG/conv_{0}.png".format(destName)
        plotKNN(inputPath, exportPath, city, attr_value, nnn, year, districtPath, neighPath, streetsPath, waterPath)
    
    if  plot_knn_dif =="yes":
        if yearPrevious == None: print ('This function will be skipped')
        else:
            inputPath = cityDestPath + "/data/KNN/GeoTIFF/conv_{0}_{1}.tif".format(destName,nnn)
            print(inputPath)
            if yearPrevious<=2020: inputPathPrevious = cityDestPath + "/data/KNN/GeoTIFF/conv_{0}_{1}_{2}.tif".format(yearPrevious,attr_value, nnn) 
            else: inputPathPrevious = cityDestPath + "/data/KNN/GeoTIFF/conv_{0}_{2}_{1}_{3}.tif".format(yearPrevious, attr_value, scenario, nnn) 
            print(inputPathPrevious)
            outPathDif = cityDestPath + "/data/KNN/GeoTIFF/dif_conv_{0}_{3}_{1}_{2}.tif".format(year,yearPrevious, attr_value, scenario)
            exportPath = cityDestPath + "/data/KNN/PNG/dif_conv_{0}_{1}_{4}_{2}_{3}.png".format(year,yearPrevious, attr_value,nnn, scenario)
            plotKNN_dif(inputPath, inputPathPrevious, outPathDif, exportPath, city, attr_value, nnn, year, yearPrevious, districtPath, neighPath, streetsPath, waterPath)

    
