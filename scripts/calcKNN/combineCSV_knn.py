import geopandas as gpd, sys, os
import pandas as pd
import glob
import numpy as np
def combineGeoJSON(geojsonPath, dst_csv, dst_vector, destNameWhole, orig_csv, attr_values,city,scenario, kernel):
    """This function combined individual GPKG files into one and produces the corresponding csv file.
    Args:
        geojsonPath (_str_): Path to folder where input GPKG are located.
        dst_csv (_str_): String for destination file name of points in csv.
        dst_vector (_str_): String for destination file name of points in gpkg.
        destNameWhole (_str_): String of file name where year and/or scenario are included.
        attr_values (_list_): List of migrant groups.
    """    
    files = glob.glob(geojsonPath + '/conv_sum_{0}_{1}_*.geojson'.format(kernel, destNameWhole))
    print(geojsonPath + '/conv_sum_{0}_{1}_*.geojson'.format(kernel, destNameWhole))
    print(files)
    if city =='cph': natives='DNK'       
    elif city =='grootams' or city =='ams': natives='NLD'     
    elif city =='crc' : natives='POL'      
    elif city =='rom' : natives='ITA'
            
    if len(attr_values) == len(files):
        
        appended_data =[]
        for i in files:
            name = i.split('{0}_'.format(destNameWhole))[-1].split('.geojson')[0]
            df = gpd.read_file(i)
                
            df['id'] = np.arange(len(df))        
            #df = df.loc[df['{}'.format(name)] > 0 ]
            df = df.set_index('id')
            appended_data.append(df)
        
        lf = pd.DataFrame()
        for df in appended_data:
            if lf.empty:
                # if the merged dataframe is empty, assign the first dataframe to it
                lf = df
            else:
                # if the merged dataframe is not empty, merge the current dataframe with it
                lf= pd.merge(lf, df, left_on='geometry', right_on='geometry', suffixes=('_left', '_right'))
        
        for i in lf.columns:
            if i not in ['geometry','lat','lon']:
                lf[i] = lf[i].fillna(0)
        """
        if city =='cph':
            lf['totalmig']= lf['EU_West']+ lf['EU_East']+ lf['EurNonEU']+ lf['MENAP']+ lf['Turkey']+ lf['OthNonWest']+ lf['OthWestern']
            lf['totalpop']= lf['totalmig'] + lf['DNK']
        elif city =='grootams' or city =='ams':
            lf['totalmig']= lf['EU West']+ lf['EU East']+ lf['Other Europe etc']+ lf['Turkey + Morocco']+ lf['Middle East + Africa']+ lf['Former Colonies']
            lf['totalpop']= lf['totalmig'] + lf['NLD']
        elif city =='crc' : 
            if scenario=='hist':lf['totalmig']= lf['EU_EFTA']+ lf['Europe_nonEU']+ lf['Other']
            else:
                lf['totalmig']= lf['EuropeEU']+ lf['EurNonEU']+ lf['Other']
            lf['totalpop']= lf['totalmig'] + lf['POL']
        elif city =='rom' : 
            lf['totalmig']= lf['BGD']+ lf['PHL']+ lf['ROU']+ lf['EU']+ lf['nonEUEu']+ lf['Africa'] + lf['America']+ lf['Asia']
            lf['totalpop']= lf['totalmig'] + lf['ITA']"""
        
        print(lf.head(2), lf.columns)
        lf = lf.rename(columns={'lat_left':'lat','lon_left':'lon'})
        lf = lf.loc[:,~lf.columns.duplicated()].copy()
        lf = lf.drop(columns=['lat_right','lon_right'])
        
        lf['eurogrid']= lf['lon'].astype(int).astype(str) + 'N' + lf['lat'].astype(int).astype(str) + 'E'
        lf = lf.loc[lf['totalpop'] > 0 ]
        print(lf.head(2), lf.columns)
        nonKNN_DF = pd.read_csv(orig_csv)
        if city=='crc': 
            nonKNN_DF = nonKNN_DF.rename(columns={'Europe_nonEU':'EurNonEU', 'EU_EFTA':'EuropeEU'})
        
        if kernel == 0: suf='100m'
        elif kernel == 1: suf = '200m'
        elif kernel == 2: suf = '300m'
        elif kernel == 3: suf = '400m'
        elif kernel == 4: suf = '500m'
        ndf = pd.merge(nonKNN_DF, lf, left_on='eurogrid', right_on='eurogrid', suffixes=('', '_{}'.format(suf)))
        
        dropCol= ['lat_{}'.format(suf),'lon_{}'.format(suf),'geometry_{}'.format(suf), 'Unnamed: 0', 'children', 'yadults', 'mobadults', 'nmobadults', 'elderly' ]

        for x in ndf.columns:
            if x in dropCol:
                ndf = ndf.drop(columns=[x])
        print(ndf.columns)
        
        if scenario != 'hist':
            for k in ndf.columns:
                if k not in ['geometry','lat','lon','eurogrid']:
                    ndf[k] = ndf[k].fillna(0)
                    print(k)
                    ndf[ndf[k]<0] = 0
        #WRITE DATAFRAME TO CSV
        ndf.to_csv(dst_csv)
        
        #ldf = gpd.GeoDataFrame(ndf , geometry='geometry', crs='EPSG:3035')
        #ldf.to_file(dst_vector, driver='GeoJSON')
    else: 
        print("Input is not correct")