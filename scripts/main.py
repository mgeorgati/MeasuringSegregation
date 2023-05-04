from process import process_Projections, process_ProjectionsTotal, process_ProjectionsNoYear

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
        from config.crc import attr_values, years_list, years_list_hist, previous_years_list, templatePath
        srcNameDef = 'Dasy_16unet_10epochspi_6AIL13_it10' #----------
    elif city == 'rom':
        from config.rom import attr_values, years_list,years_list_hist, previous_years_list, templatePath
        srcNameDef = 'Dasy_16unet_10epochspi_12AIL5_it5' #----------
    
    for scenario in ['bch', 'bs']: #'bs', 'war','re' 'bch', 'eur','re', 'hist'
        if scenario =='hist': years_list = years_list_hist
        
        for i in range(len(years_list)):
            year = years_list[i]
            if len(previous_years_list) == len(years_list):
                yearPrevious = previous_years_list[i] # This is for the KNN difference
            else: yearPrevious= None

            for attr_value in attr_values:
                process_Projections(city, scenario, attr_value, year, srcNameDef,
                        processRawOutput ='no', init_calc_dif='no', fix_negative_values ='no',
                        init_raster_shp ='no',  # These need to be executed for all groups first 
                        plotMaps100 = 'no',
                        calc_KNNneigh = 'no', templatePath = templatePath, yearPrevious = yearPrevious, calc_Conv='no', plot_knn = 'no', plot_knn_dif= 'yes')
            
            # these need to executed after all the tiffs have been renamed for all attr_values
            process_ProjectionsTotal(city, scenario, attr_values, year,
                        init_shp_gpkg='no',  init_point_cell ='no', init_calc_summary ='no', init_calc_dis='no', 
                        )
        process_ProjectionsNoYear(city, attr_values, scenario, create_GIFs='no')

city = 'ams'              
main(city)