from osgeo import ogr, gdal, osr
import  os
import numpy as np
import itertools

def pixelOffset2coord(raster, xOffset,yOffset):
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0] + 50
    originY = geotransform[3] - 50
    pixelWidth = geotransform[1] 
    pixelHeight = geotransform[5] 
    coordX = originX+pixelWidth*xOffset
    coordY = originY+pixelHeight*yOffset
    return coordX, coordY

def raster2array(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    #band = band.Fill(NO_DATA_VALUE)
    #band =band.SetNoDataValue(0)
    array = band.ReadAsArray()
    array = np.nan_to_num(array,0)
    return array

def array2shp(array,outSHPfn,rasterfn, attr_value):

    # max distance between points
    raster = gdal.Open(rasterfn)
    
    geotransform = raster.GetGeoTransform()
    pixelWidth = geotransform[1]

    # wkbPoint
    shpDriver = ogr.GetDriverByName("GeoJSON")
    if os.path.exists(outSHPfn):
        shpDriver.DeleteDataSource(outSHPfn)
    outDataSource = shpDriver.CreateDataSource(outSHPfn)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035)
    

    outLayer = outDataSource.CreateLayer("{}".format(outSHPfn), srs = srs, geom_type=ogr.wkbPoint )
    featureDefn = outLayer.GetLayerDefn()
    
    outLayer.CreateField(ogr.FieldDefn("{}".format(attr_value), ogr.OFTReal))
    outLayer.CreateField(ogr.FieldDefn("lat".format(attr_value), ogr.OFTReal))
    outLayer.CreateField(ogr.FieldDefn("lon".format(attr_value), ogr.OFTReal))
    # array2dict
    point = ogr.Geometry(ogr.wkbPoint)
    row_count = array.shape[0]
    for ridx, row in enumerate(array):
        if ridx % 100 == 0:
            print ("{0} of {1} rows processed".format(ridx, row_count))
        for cidx, value in enumerate(row):
            Xcoord, Ycoord = pixelOffset2coord(raster,cidx,ridx)
            point.AddPoint(Xcoord, Ycoord)
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(point)
            if value == np.nan: 
                val = 0
            #elif value < 0: 
                #val = 0
            else: 
                val = float("{:.2f}".format(value)) #np.round(value, 2)
            
            outFeature.SetField("{}".format(attr_value), val)
            outFeature.SetField("lat", Xcoord)
            outFeature.SetField("lon", Ycoord)
            outLayer.CreateFeature(outFeature)
            outFeature.Destroy()
    #outDS.Destroy()

def mainRaster(rasterfn,outSHPfn, attr_value):
    array = raster2array(rasterfn)
    array2shp(array,outSHPfn,rasterfn, attr_value)