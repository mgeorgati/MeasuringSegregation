import os

import numpy as np
import rasterio
import rasterio.plot
import sys,os
from scipy.ndimage import  generic_filter

sys.path.append('./')  
from basic.conversions import writeRaster

from plotting.plotRaster import plot_map

def calcConv(inputPath, raster_file, nnn, outPath, templatePath):
    
    templ = rasterio.open(templatePath)
    temp = templ.read(1)
    
    waterPath = rasterio.open(raster_file)
    water = waterPath.read(1)
    water = np.where(water>0.3, water, 0)
    mask = temp * water
    mask = np.where(mask==1, np.nan, mask)
    
    src = rasterio.open(inputPath)
    arr = src.read(1)
    arr[np.isnan(mask)] = np.nan
    
    kernel0 = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]) #3x3 ellipsoidal
    kernel1 = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) #3x3 rectangular
    
    kernel2 = np.array([[0, 0, 1, 0, 0], 
                        [0, 1, 1, 1, 0], 
                        [1, 1, 1, 1, 1],
                        [0, 1, 1, 1, 0], 
                        [0, 0, 1, 0, 0]]) #5x5 ellipsoidal
    
    kernel3 = np.array([[1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1]]) #5x5 rectangular
    
    kernel4 = np.array([[0, 0, 0, 1, 0, 0, 0], 
                        [0, 1, 1, 1, 1, 1, 0], 
                        [0, 1, 1, 1, 1, 1, 0], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [0, 1, 1, 1, 1, 1, 0], 
                        [0, 1, 1, 1, 1, 1, 0], 
                        [0, 0, 0, 1, 0, 0, 0]]) #7x7 ellipsoidal

    kernel5 = np.array([[1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1]]) #7x7 rectangular

    kernel6 = np.array([[0, 0, 0, 0, 1, 0, 0, 0, 0], 
                        [0, 0, 1, 1, 1, 1, 1, 0, 0], 
                        [0, 1, 1, 1, 1, 1, 1, 1, 0], 
                        [0, 1, 1, 1, 1, 1, 1, 1, 0], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [0, 1, 1, 1, 1, 1, 1, 1, 0], 
                        [0, 1, 1, 1, 1, 1, 1, 1, 0],
                        [0, 0, 1, 1, 1, 1, 1, 0, 0], 
                        [0, 0, 0, 0, 1, 0, 0, 0, 0]]) #9x9 ellipsoidal
    
    kernel7 = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1]]) #9x9 rectangular
    
    c0 = generic_filter(arr, np.nansum, footprint=kernel0, mode='constant', cval=np.NaN)
    c0 = np.where(c0>=nnn, 0, 1)
    c1 = generic_filter(arr, np.nansum, footprint=kernel1, mode='constant', cval=np.NaN)
    c1 = np.where(c1>=nnn, 0, 1)
    c2 = generic_filter(arr, np.nansum, footprint=kernel2, mode='constant', cval=np.NaN)
    c2 = np.where(c2>=nnn, 0, 1)
    c3 = generic_filter(arr, np.nansum, footprint=kernel3, mode='constant', cval=np.NaN)
    c3 = np.where(c3>=nnn, 0, 1)
    c4 = generic_filter(arr, np.nansum, footprint=kernel4, mode='constant', cval=np.NaN)
    c4 = np.where(c4>=nnn, 0, 1)
    c5 = generic_filter(arr, np.nansum, footprint=kernel5, mode='constant', cval=np.NaN)
    c5 = np.where(c5>=nnn, 0, 1 )
    c6 = generic_filter(arr, np.nansum, footprint=kernel6, mode='constant', cval=np.NaN)
    c6 = np.where(c6>=nnn, 0, 1)
    c7 = generic_filter(arr, np.nansum, footprint=kernel7, mode='constant', cval=np.NaN)
    print(np.max(c7))
    c7 = np.where(c7>=nnn, 0, 1)
    c = c0 + c1 + c2 + c3 + c4 + c5 + c6 + c7
    cf = np.where(temp != 0, c, np.nan)
    cf[np.isnan(mask)] = np.nan  
    writeRaster(inputPath, outPath, cf)
    #return cf

def plotKNN(srcPath, exportPath, city, attr_value, thres, year, districtPath, polyPath, streetsPath, waterPath):
    # Plot the population distribution of the predictions 
    if not os.path.exists(exportPath):
        print("----- Step #1: Plotting Population Distribution -----")
        title ="Egocentric Neighbourhoods - {1} \n {0}, KNN:{2}".format(year, attr_value, thres)
        LegendTitle = "Steps"
        plot_map(city,'KNN', srcPath, exportPath, title, LegendTitle, attr_value, districtPath = districtPath, neighPath = polyPath, streetsPath= streetsPath, waterPath = waterPath, invertArea = None, addLabels=True)     
           
def plotKNN_dif(inputPath, inputPathPrevious, outPathDif, exportPath, city, attr_value, thres, year, yearPrevious, districtPath, polyPath,streetsPath, waterPath):
    
    src = rasterio.open(inputPath)
    arr = src.read(1)
    
    srcPrevious = rasterio.open(inputPathPrevious)
    arrPrevious = srcPrevious.read(1)
       
    dif = arr - arrPrevious
    writeRaster(inputPath, outPathDif, dif)
    
    # Plot the population distribution of the predictions 
    if not os.path.exists(exportPath):
        print("----- Step #1: Plotting Population Distribution -----")
        title ="Egocentric Neighbourhoods - {3} \n Difference between {0} and {1} (KNN:{2})".format(yearPrevious, year, thres, attr_value)
        LegendTitle = "Steps"
        plot_map(city,'dif_KNN', outPathDif, exportPath, title, LegendTitle, attr_value, districtPath = districtPath, neighPath = polyPath, streetsPath = streetsPath, waterPath = waterPath, invertArea = None, addLabels=True)     

