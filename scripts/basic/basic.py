import shutil,os

## ## ## ## ## ----- CREATE NEW FOLDER  ----- ## ## ## ## ##
def createFolder(path):
    if not os.path.exists(path):
        print("------------------------------ Creating Folder : {} ------------------------------".format(path))
        os.makedirs(path)
    else: 
        print("------------------------------ Folder already exists------------------------------")
        
def renameCopyTif(srcPath, srcName, destPath, destName):
    
    src_dir = srcPath + srcName + '.tif'
    print(src_dir)
    dst_dir = destPath + destName + '.tif'
    shutil.copy(src_dir , dst_dir)

from osgeo import gdal  

def progress_cb(complete, message, cb_data):
    '''Emit progress report in numbers for 10% intervals and dots for 3%'''
    if int(complete*100) % 10 == 0:
        print(f'{complete*100:.0f}', end='', flush=True)
    elif int(complete*100) % 3 == 0:
        print(f'{cb_data}', end='', flush=True)
        
def vrt2tifGDAL(raster_file, temp_outputfileVRT, outputfile):
    data = gdal.Open(raster_file)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0] 
    maxy = geoTransform[3] 
    maxx = minx + geoTransform[1] * data.RasterXSize 
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None
    bbox = (minx,maxy,maxx,miny)
    #Clip 
    gdal.Translate(outputfile, temp_outputfileVRT, projWin=bbox, callback=progress_cb, callback_data='.')
    
