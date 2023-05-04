from osgeo import gdal, osr
import numpy as np


def readRaster(file):
    raster = gdal.Open(file)
    band = raster.GetRasterBand(1)
    rastergeo = raster.GetGeoTransform()
    dataset = np.array(band.ReadAsArray(),dtype=np.float64) #dtype=np.float64
    dataset = dataset.astype(np.float64)
    dataset[dataset < -999999] = np.NaN
    dataset = np.reshape(dataset, dataset.shape + (1,))
    
    return dataset, rastergeo

def writeRaster(dataset, rastergeo, fraster):
    driver = gdal.GetDriverByName('GTiff')
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(3035) # WGS-84
    outRaster = driver.Create(fraster, dataset.shape[1], dataset.shape[0], 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((rastergeo[0], rastergeo[1], 0, rastergeo[3], 0, rastergeo[5]))
    outRaster.SetProjection(srs.ExportToWkt())
    outband = outRaster.GetRasterBand(1)
    outband.SetNoDataValue(-9999)
    outband.WriteArray(dataset)
    outband.FlushCache()
    outband = None