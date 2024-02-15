import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rs 
from basic.osgeoutils import readRaster, writeRaster

def update_frame(gdf_points, attr_value, q):
    for index, row in gdf_points.iterrows():
        if row[attr_value] < 0:
            lat = row['lat']
            lon = row['lon']
            
           
            if (lat-q) in gdf_points['lat'].values and lon in gdf_points['lon'].values:
                left = gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value].iloc[0]
                #print(left)
                if left >= abs(row[attr_value]) :
                    #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    #print('Before', gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    
                    gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value] = left + row[attr_value]
                    gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                    
                    #print('Updated left', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    #print('Updated left', gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    
                
            elif lat in gdf_points['lat'].values and lon+q in gdf_points['lon'].values:
                up = gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value].iloc[0]
                
                if up >= abs(row[attr_value]):
                    #print('Before', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])
                    #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    
                    
                    gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value] = up + row[attr_value]
                    gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                    
                    #print('Updated up', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    #print('Updated up', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])

            elif lat + q in gdf_points['lat'].values and lon+q in gdf_points['lon'].values:
                rgt = gdf_points.loc[(gdf_points['lat'] == lat +  q) & (gdf_points['lon'] == lon + q), attr_value].iloc[0]
                
                if rgt >= abs(row[attr_value]) :
                    #print('Before', gdf_points.loc[(gdf_points['lat'] == lat+  q) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])
                    #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    
                    gdf_points.loc[(gdf_points['lat'] == lat+  q) & (gdf_points['lon'] == lon + q), attr_value] = rgt + row[attr_value]
                    gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                    
                    #print('Updated rgt', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    #print('Updated rgt', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat+  q) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])
                
                    
            elif lat in gdf_points['lat'].values and lon-q in gdf_points['lon'].values:
                down = gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value].iloc[0]
                
                if down >= abs(row[attr_value]) :
                    #print('Before', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value].iloc[0])
                    #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    
                    gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value] = down + row[attr_value]
                    gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                    
                    #print('Updated down', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                    #print('Updated down', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value].iloc[0])
            #else: print('no updates')
    return gdf_points

def fixNegatives(pointsPath, attr_value, dst_path):
    gdf_points = gpd.read_file(pointsPath, crs="EPSG:3035")
    print('Starting iteration for ', attr_value)
    print(gdf_points[attr_value].sum())
    print(gdf_points.loc[gdf_points[attr_value] >0, attr_value].sum())
    print(gdf_points.loc[gdf_points[attr_value] <0, attr_value].sum())
    df = gdf_points.copy()
    
    for i in range(1,20):
        q= i*100
        ndf = update_frame(df, attr_value, q)
        df.update(ndf)
        
    print(df.loc[df[attr_value] >0, attr_value].sum())
    print(df.loc[df[attr_value] <0, attr_value].sum())                      
    print('Saving file for', attr_value)
    
    df.to_file(dst_path, driver='GeoJSON', crs='EPSG:3035')


def num_pieces(num, length):  
    # A function that splits the num to length pieces maintating the sum 
    
    ot = list(range(1,length+1))[::-1]
    #print(ot, num, length)
    all_list = []
    for i in range(length-1):
        n = np.random.randint(1, num-ot[i])
        all_list.append(n)
        num -= n
        
    all_list.append(num) 
    return all_list

def removeNegatives(popflat, pop, listNegatives, nonNegativePop):
    
    #popsum = pop[pop>0].sum()
    p = np.absolute(nonNegativePop.flatten()/nonNegativePop.sum())
     
    #p = np.nan_to_num(p, posinf=0, neginf=0, nan=0)
    #print(p.sum(),popsum)
    #p = np.nan_to_num(p/p.sum())
    #print(C)
    for i in listNegatives:
        B = np.where(popflat >= np.abs(i))[0].tolist()
        

        #p /= p.sum() #fix for: Probabilities didn't sum to 1
        removersPos = np.random.choice(B, 1).tolist()
        #print(removersPos)
        #print('cellValue:', popflat[removersPos[0]], 'pos:', removersPos[0], 'value to be replaced with:',i)
        if popflat[removersPos] >= np.abs(i):
            #print('cellValue:', popflat[removersPos], 'pos:', removersPos, 'value to be replaced with:',i)
            popflat[removersPos] = popflat[removersPos] + i
            #print('cellValue:', popflat[removersPos], 'pos:', removersPos, 'value to be replaced with:',i)
            listNegatives.remove(i)
            #else:
                #print('naon')
                #break
    return popflat

import multiprocessing
from datetime import datetime 

def multiple(popflat, a, pop, listNegatives):
    # Create a list of numbers
    numbers = listNegatives

    # Create a multiprocessing.Queue to store the output
    output = multiprocessing.Queue()

    # Divide the list of numbers into chunks
    num_chunks = 4
    chunk_size = len(numbers) // num_chunks
    chunks = [numbers[i:i+chunk_size] for i in range(0, len(numbers), chunk_size)]

    # Create a list of processes
    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=removeNegatives, args=(popflat, a, pop, listNegatives))
        processes.append(p)
    # Start the processes
    for p in processes:
        p.start()
    
    # Wait for the processes to finish
    for p in processes:
        p.join()
    
    # Get the output from the queue
    results = []
    results.append(popflat)
    while not output.empty():
        result = output.get()
        results.append(result)

    # Print the results
    print(results)
    return results

def removeRandomPeople(src_path, src_file_previous, fraster):
    disseverdatasetA, rastergeo = readRaster(src_file_previous)
    src_previous = rs.open(src_file_previous)
    pop = src_previous.read()
    pop = np.round(pop,0)
    pop = pop.astype(np.int64)
    pop = np.absolute(pop)
    
    a = pop.shape[1] * pop.shape[2]
    
    src = rs.open(src_path)
    arr = src.read() 
    arr = np.nan_to_num(arr, nan=0)
    arr = np.round(arr,0)
    arr = arr.astype(np.int64)
    
    popflat = arr.flatten()
    
    nonNegativePop = popflat[popflat>0]
    
    num = np.abs(popflat[popflat<0].sum())
    length = len(popflat[popflat>0]) # number of cells with positive values
    print('arr initial', popflat.sum(), 'positive:', popflat[popflat >0].sum(), 'negative:', popflat[popflat <0].sum())
    
    if num!= 0:
        listNegatives = []
        for x in popflat:
            if x < 0:
                listNegatives.append(x)  

        B = np.where(popflat > 0)[0].tolist()
        
        listNegatives = sorted(listNegatives) #[0:10]
        #print(listNegatives)
        print(len(listNegatives), sum(listNegatives), min(listNegatives) )
        """for x in listNegatives:
            if x < -156:
                listNegatives.remove(x)
                print('1:', len(listNegatives), sum(listNegatives))
                if (x%4) ==0:
                    print('2:', x/4)
                    listNegatives.append(x/4)
                    listNegatives.append(x/4)
                    print('3:', len(listNegatives), sum(listNegatives))
                else:
                    print('second', x-1/4)
                    listNegatives.append(x+1/4)
                    listNegatives.append(x+1/4)
                    listNegatives.append(-1)
                    print('4:', len(listNegatives), sum(listNegatives))

        print(len(listNegatives), sum(listNegatives), min(listNegatives), len([x for x in listNegatives if x < -100]) )"""
        #if max(B) < max(listNegatives):print('aaaaaaaaa')
        
        while len(listNegatives)>0:
            removeNegatives(popflat, pop, listNegatives, nonNegativePop)
            print(len(listNegatives), sum(listNegatives) )
            #print(popflat.sum(), 'positive:', popflat[popflat >0].sum(), 'negative:', popflat[popflat <0].sum())
        popflat[popflat<0] = 0
        print(popflat.sum(), 'positive:', popflat[popflat >0].sum(), 'negative:', popflat[popflat <0].sum())
        print(pop.shape[1], pop.shape[2])
        dataset = popflat.reshape(pop.shape[1], pop.shape[2]) 
        writeRaster(dataset, rastergeo, fraster)
    else: 
        import shutil
        shutil.copy(src_path, fraster)
    






"""
def fixNegatives(pointsPath, attr_value, dst_path):
    gdf_points = gpd.read_file(pointsPath, crs="EPSG:3035")
    print('Starting iteration for ', attr_value)
    print(gdf_points[attr_value].sum())
    print(gdf_points.loc[gdf_points[attr_value] >0, attr_value].sum())
    for index, row in gdf_points.iterrows():
        if row[attr_value] < 0:
            lat = row['lat']
            lon = row['lon']
            q=0
            
            while q < 400: #000
                q += 100
                if (lat-q) in gdf_points['lat'].values and lon in gdf_points['lon'].values:
                    left = gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value].iloc[0]
                    #print(left)
                    if left >= abs(row[attr_value]) :
                        #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        #print('Before', gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        
                        gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value] = left + row[attr_value]
                        gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                        
                        #print('Updated left', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        #print('Updated left', gdf_points.loc[(gdf_points['lat'] == lat - q) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        
                    
                elif lat in gdf_points['lat'].values and lon+q in gdf_points['lon'].values:
                    up = gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value].iloc[0]
                    
                    if up >= abs(row[attr_value]):
                        #print('Before', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])
                        #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        
                        
                        gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value] = up + row[attr_value]
                        gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                        
                        #print('Updated up', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        #print('Updated up', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])

                elif lat + q in gdf_points['lat'].values and lon+q in gdf_points['lon'].values:
                    rgt = gdf_points.loc[(gdf_points['lat'] == lat +  q) & (gdf_points['lon'] == lon + q), attr_value].iloc[0]
                    
                    if rgt >= abs(row[attr_value]) :
                        #print('Before', gdf_points.loc[(gdf_points['lat'] == lat+  q) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])
                        #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        
                        gdf_points.loc[(gdf_points['lat'] == lat+  q) & (gdf_points['lon'] == lon + q), attr_value] = rgt + row[attr_value]
                        gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                        
                        #print('Updated rgt', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        #print('Updated rgt', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat+  q) & (gdf_points['lon'] == lon + q), attr_value].iloc[0])
                    
                        
                elif lat in gdf_points['lat'].values and lon-q in gdf_points['lon'].values:
                    down = gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value].iloc[0]
                    
                    if down >= abs(row[attr_value]) :
                        #print('Before', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value].iloc[0])
                        #print('Before', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        
                        gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value] = down + row[attr_value]
                        gdf_points.loc[(gdf_points['lat'] == lat ) & (gdf_points['lon'] == lon), attr_value] = 0
                        
                        #print('Updated down', gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon), attr_value].iloc[0])
                        #print('Updated down', lat, lon, gdf_points.loc[(gdf_points['lat'] == lat) & (gdf_points['lon'] == lon - q), attr_value].iloc[0])
                else: print('no updates')
            #print('---------------------')
                  

    print(gdf_points[attr_value].sum())
    if gdf_points[attr_value].any() < 0:
        print('Further action is needed')      
    print('Saving file for', attr_value)
    
    gdf_points.to_file(dst_path, driver='GeoJSON', crs='EPSG:3035') """


