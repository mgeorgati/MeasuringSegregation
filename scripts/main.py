from process import process_Projections, process_ProjectionsTotal, process_ProjectionsNoYear
from processKNN import process_KNN, process_KNN_total 

def main(city):
    if city == 'grootams':
        from config.grootams import attr_values, years_list, previous_years_list, templatePath
        srcNameDef = 'Dasy_16unet_10epochspi_7AIL10_it10' #---------- #Dasy_16unet_10epochspi_8AIL5_it10 : the 1st with 2020totalpop training
    elif city == 'ams':
        from config.ams import attr_values, years_list, years_list_hist, previous_years_list, templatePath
        srcNameDef = 'Dasy_16unet_10epochspi_8AIL5_it10' #----------
    elif city == 'cph':
        from config.cph import attr_values, years_list, previous_years_list, templatePath
        srcNameDef = 'Dasy_16unet_10epochspi_5AIL5_it10' #----------
    elif city == 'crc':
        from config.crc import attr_values, years_list, years_list_hist, previous_years_list, templatePath, attr_values_old
        srcNameDef = 'Dasy_16unet_10epochspi_6AIL13_it10' #----------
    elif city == 'rom':
        from config.rom import attr_values, years_list,years_list_hist, previous_years_list, templatePath
        srcNameDef = 'Dasy_16unet_10epochspi_12AIL5_it5' #----------
    

    for scenario in [ 'hist']: #'bs', 'war','re' 'bch', 'eur','re', 'hist', 'bch','bs'
        if scenario =='hist': 
            years_list = years_list_hist
            if city == 'crc':  attr_values = attr_values_old
        for i in range(len(years_list)):
            year = years_list[i]
            if len(previous_years_list) == len(years_list):
                yearPrevious = previous_years_list[i] # This is for the KNN difference
            else: yearPrevious= None

            for attr_value in attr_values:
                process_Projections(city, scenario, attr_value, year, srcNameDef,
                        processRawOutput ='no',  init_fix_null='no',  init_calc_dif='no', fix_negative_values ='no',
                        init_raster_shp ='no',  # These need to be executed for all groups first ,
                        init_shp_to_raster = 'no',  # These need to be executed after the calculation of the gridcells just for totalpop and totalmig
                        plotMaps100 = 'no',
                        )
                
                process_KNN(city, scenario, attr_value, year, srcNameDef,
                        calc_KNNneigh = 'no', templatePath = templatePath, yearPrevious = yearPrevious, calc_Conv='no', plot_knn = 'no', plot_knn_dif= 'no',
                        estimate_sum_knn = 'yes', init_raster_shp= 'no') #HEEEERRE
            
            # these need to executed after all the tiffs have been renamed for all attr_values
            process_ProjectionsTotal(city, scenario, attr_values, year,
                        init_shp_gpkg='no',  init_point_cell ='no', init_calc_summary ='no', init_calc_dis='no', calcSums= 'no'
                        )

            process_KNN_total(city,scenario, attr_values, year, init_shp_gpkg= 'no', removeFilles='no')
        
        process_ProjectionsNoYear(city, attr_values, scenario, create_GIFs='no')

city = 'rom'              
main(city)