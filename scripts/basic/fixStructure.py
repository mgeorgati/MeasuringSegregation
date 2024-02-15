import os, sys, subprocess
import shutil
from pathlib import Path
import glob
sys.path.append('./') 
from config.config import python_scripts_folder_path
from basic.basic import renameCopyTif, vrt2tifGDAL, createFolder
from basic.osgeoutils import readRaster, writeRaster
import rasterio as rs
import numpy as np
def processProjections(city, scenario, attr_value, year, srcNameDef, srcPath, cityDestPath):
    print('----- Running process for {0}, scenario:{1}, attr_value:{2}, in {3} -----'.format(city, scenario, attr_value, year))
    
    # YOU NEED TO DEFINE THIS!!!!!!!!!!!!!!!!!
    srcName = 'dissever01_{0}_CLF_LR0001_{1}_{2}_{4}_{3}'.format(scenario, year, city, attr_value, srcNameDef)
    if city=='rom' and year<=2020 :
        destName = '{1}_{2}'.format(scenario, year, attr_value)
    else:
        destName = '{1}_{0}_{2}'.format(scenario, year, attr_value)
    
    if city == 'ams':
        from config.grootams import srcPath_alt, raster_file_small, templateAms
        fixAms(city, scenario, year, attr_value, srcNameDef, 'yes', 'yes', srcPath_alt, raster_file_small, templateAms)
    
    if city == 'grootams':
        dictAttrValues = {'totalpop':'totalpop', 'NLD':'NLD', 'EU West':'EU_West', 'EU East':'EU_East', 'Other Europe etc':'OthEurope', 
                              'Turkey + Morocco':'TurMor', 'Middle East + Africa': 'ME_Africa', 'Former Colonies': 'colonies'}
        if attr_value in dictAttrValues.keys(): 
            popValue = dictAttrValues.get(attr_value)
            print(attr_value, popValue)
        
        srcName = 'dissever01_{0}_CLF_LR0001_{1}_{2}_{4}_{3}'.format(scenario, year, city, popValue, srcNameDef)
    print(srcPath)
    destPath = cityDestPath + '/data/GeoTIFF_dif/'#
    createFolder(destPath)
    renameCopyTif(srcPath, srcName, destPath, destName)
    
    print('| Output sucessfully produced in:', cityDestPath + '/data/GeoTIFF_dif/')


def fixAms(city, scenario, year, attr_value, srcNameDef, removeOuterValues, fixClipped, srcPath_alt, raster_file_small, templateAms):
    dictAttrValues = {'totalpop':'totalpop', 'NLD':'NLD', 'EU West':'EU_West', 'EU East':'EU_East', 'Other Europe etc':'OthEurope', 
                              'Turkey + Morocco':'TurMor', 'Middle East + Africa': 'ME_Africa', 'Former Colonies': 'colonies'}

            
    if attr_value in dictAttrValues.keys(): 
        popValue = dictAttrValues.get(attr_value)
        print(attr_value, popValue)
    
    sfiles_alt = glob.glob(srcPath_alt + '/*{0}*{1}*{2}.tif'.format(scenario, year, popValue))
    for x in sfiles_alt:
        path = Path(x)
        name = path.stem
        if removeOuterValues =='yes':
            output = os.path.dirname(os.path.dirname(srcPath_alt)) + '/grootams_clipped/'
            createFolder(output)
            print("------------------------------ Grootams clipped to municipality level ------------------------------")
            cmds = 'python {0}/gdal_calc.py -A "{1}" -B "{2}" --A_band=1 --B_band=1 --outfile="{3}" --calc="(A*B)"'.format(python_scripts_folder_path, srcPath_alt + name + '.tif', templateAms, output+ name + '.tif' )
            print(cmds)
            subprocess.call(cmds, shell=True)
            
        if fixClipped=='yes':
            createFolder(os.path.dirname( os.path.dirname(srcPath_alt)) + '/{}/'.format(city))
            vrt2tifGDAL(raster_file_small, os.path.dirname( os.path.dirname(srcPath_alt)) + '/grootams_clipped/' + name + '.tif' , os.path.dirname( os.path.dirname(srcPath_alt)) + '/{}/'.format(city) + 'dissever01_{0}_CLF_LR0001_{1}_{2}_{4}_{3}'.format(scenario, year, city, attr_value, srcNameDef) + '.tif')
        
def calcDifference( srcPath, src_path_previous, dest_path):    
    
    
    cmds = 'python {0}/gdal_calc.py -A "{1}" -B "{2}" --A_band=1 --B_band=1 --outfile="{3}" --calc="(A+B)"'.format(
        python_scripts_folder_path, srcPath, src_path_previous , dest_path)
    print(cmds)
    subprocess.call(cmds, shell=True)

def fixNull( srcPath, dest_path):    
    
    disseverdatasetA, rastergeo = readRaster(srcPath)
    src_previous = rs.open(srcPath)
    pop = src_previous.read()
    dataset = np.nan_to_num(pop, nan=0)
    dataset = dataset.reshape(pop.shape[1], pop.shape[2])
    print(dataset.shape)
    writeRaster(dataset, rastergeo, dest_path)
    
            
        