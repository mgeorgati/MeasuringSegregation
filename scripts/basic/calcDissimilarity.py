import geopandas as gpd, os, numpy as np 

def calcDissimilarity(srcPath, dissimFile, year, selection, city):
    """_summary_

    Args:
        srcPath (_type_): _description_
        dissimFile (_type_): _description_
        year (_type_): _description_
        selection (_type_): _description_
        totalpop (_type_): _description_
        city (_type_): _description_
    """    
    df = gpd.read_file(srcPath, driver='GeoJSON',crs="EPSG:3035")
    for col in df.columns:
        if col != 'geometry':
            
            df[col] = df[col].replace(np.nan, 0)
    
    for k in selection:
        if k !=  'totalpop':
            df['restPop'] = df['totalpop'] - df['{}'.format(k)]
            df['D_{}'.format(k)] = 0.5 * np.sum((np.absolute((df['{}'.format(k)]/df['{}'.format(k)].sum()) - (df['restPop']/df['restPop'].sum()))))
            d90 = round(df['D_{}'.format(k)].mean(), 4)

            if os.path.exists(dissimFile):
                with open(dissimFile, 'a') as myfile:
                    myfile.write(str(year) + ';' + k + ';' + str(d90) + '\n')       
            else:
                with open(dissimFile , 'w+') as myfile:
                    myfile.write('Dissimilarity Measures in {} \n'.format(city))
                    myfile.write('Region of Origin;{}\n'.format(year))
                    myfile.write(str(year) + ';' + k + ';' + str(d90) + '\n')




