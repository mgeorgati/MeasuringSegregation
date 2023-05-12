import numpy as np, rasterio ,os, pandas as pd,sys
from scipy.ndimage import  generic_filter
sys.path.append('./')  
from basic.conversions import writeRaster
from basic.summaryStat import append_df_to_excel
def estimateKNN(inputPath, raster_file, templatePath, cityDestPath, destName):   
    templ = rasterio.open(templatePath)
    temp = templ.read(1)
    
    waterPath = rasterio.open(raster_file)
    water = waterPath.read(1)
    water = np.where(water>0.3, water, 0)
    mask = temp * water
    mask = np.where(mask==1, np.nan, mask)
    
    src = rasterio.open(inputPath)
    arr = src.read(1)
    #arr[np.isnan(mask)] = np.nan
    
    kernel1 = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) #3x3 rectangular
    
    kernel2 = np.array([[1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1]]) #5x5 rectangular

    kernel3 = np.array([[1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1]]) #7x7 rectangular
 
    kernel4 = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1]]) #9x9 rectangular
    
    kernel5 = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]) #9x9 rectangular
    
    kernels = [kernel1, kernel2, kernel3, kernel4, kernel5]
    
    for i in range(len(kernels)):
        outPath = cityDestPath + "/data/KNN/SUMs/conv_sum_{1}_{0}.tif".format(destName,i)
        c0 = generic_filter(arr, np.nansum, footprint=kernels[i], mode='constant', cval=np.NaN)
        writeRaster(inputPath, outPath, c0)

def calc_summaryKNN_sums(cityDestPath, city, year, scenario, attr_values, excelFile):
    ndf = pd.DataFrame(columns=['Distance (m)','Year', 'Group', '0-25','25-50','50-75','75-100','100-200','200-500','>500' ])
    for k in range(0,8):
        if k ==0 : d = 100
        elif k==1 : d= 150
        elif k==2 : d= 200
        elif k==3 : d= 250
        elif k==4 : d= 300
        elif k==5 : d= 350
        elif k==6 : d= 400
        elif k==7 : d= 450
        for i in attr_values:
            if scenario == 'hist':
                inputPath = cityDestPath + "/data/KNN/SUMs/conv_sum_{0}_{1}_{3}.tif".format(k, year, scenario, i)
            else:
                inputPath = cityDestPath + "/data/KNN/SUMs/conv_sum_{0}_{1}_{2}_{3}.tif".format(k, year, scenario, i)
            src = rasterio.open(inputPath)
            arr = src.read(1)

            length0 = len(arr [(arr < 25) & (arr > 0)]) /len(arr[arr > 0]) *100
            length1 = len(arr [(arr < 50) & (arr >= 25)]) /len(arr[arr > 0]) *100
            length2 = len(arr [(arr < 75) & (arr >= 50)]) /len(arr[arr > 0]) *100
            length3 = len(arr [(arr < 100) & (arr >= 75)]) /len(arr[arr > 0]) *100
            length4 = len(arr [(arr < 200) & (arr >= 100)]) /len(arr[arr > 0]) *100
            length5 = len(arr [(arr < 500) & (arr >= 200)]) /len(arr[arr > 0]) *100
            length6 = len(arr [(arr > 500) ]) /len(arr[arr > 0]) *100

            if ndf.size == 0:
                ndf.loc[1] = [d,year, i, length0, length1, length2, length3, length4, length5, length6]
            else: 
                ndf.loc[-1] = [d,year, i, length0, length1, length2, length3, length4, length5, length6]
                ndf.index = ndf.index + 1  # shifting index
                #ndf = ndf.sort_index()  # sorting by index
                # adding a row
            
            #
    append_df_to_excel(excelFile, ndf, 'Sheet1')
    """
    print('edo', length0, length1, length2, length4, length5)
    if os.path.exists(excelFile):
        with open(excelFile, 'a') as myfile:
            myfile.write(str(destName) + ';' + 'd0' + ';'  '\n')  
            myfile.write(str('km1') + ';' + str(np.round(length0,2)) + ';'  '\n')
            myfile.write(str('km2') + ';' + str(np.round(length1,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length2,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length3,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length4,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length5,2)) + ';'  '\n')     
    else:
        with open(excelFile , 'w+') as myfile:
            myfile.write('Egocentric neighbourhoods in {} \n'.format(city))
            myfile.write('Region of Origin;{}'.format(destName) + ';' + 'length0' + ';'  '\n')
            myfile.write(str('km1') + ';' + str(np.round(length0,2)) + ';'  '\n')
            myfile.write(str('km2') + ';' + str(np.round(length1,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length2,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length3,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length4,2)) + ';'  '\n')
            myfile.write(str(destName) + ';' + str(np.round(length5,2)) + ';'  '\n')"""