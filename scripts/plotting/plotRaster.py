import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import rasterio, sys
import rasterio.plot
from matplotlib.colors import ListedColormap
sys.path.append('./') 
from plotting.defineBins import defineBinsRaster

def plot_map(city, evalType, srcPath, exportPath, title, LegendTitle, attr_value, districtPath, neighPath, streetsPath, waterPath, invertArea, addLabels=True):
    src = rasterio.open(srcPath)
    pop = src.read(1)
    pop= np.nan_to_num(pop, nan=0)
    pop = pop.astype(np.int64)
    pop[(np.where(pop == -9999))] = 0
    pop[(np.where(pop <0 ))] = 0
    
    valMax = np.round(np.max(pop), 2)
    valMin = np.round(np.min(pop), 2)
    mean = np.round(np.mean(pop), 2)
    print(np.max(pop), np.min(pop))
    fig, ax = plt.subplots(figsize=(20, 20),facecolor='white') #50, 50
    cmap, norm, legend_labels = defineBinsRaster(evalType, attr_value, valMin, valMax, mean, city)
    #hist=np.asarray(np.histogram(no_outliers, bins=bins, density=True))
    #values = hist[1]
    #print(values)
    #b= np.round(values, decimals=2)
    if districtPath:
        if city == 'crc':
            srcfile = gpd.read_file(districtPath, encoding ="latin-1" ).to_crs('EPSG:3035')
        else: srcfile = gpd.read_file(districtPath )
        srcfile.plot(ax=ax, facecolor='none', edgecolor='#000000', linewidth=0.8,  zorder=17 ) #alpha=0.8,
        if addLabels:
            srcfile['coords']= srcfile['geometry'].apply(lambda x: x.representative_point().coords[:])
            srcfile['coords'] = [coords[0] for coords in srcfile['coords']]
            for idx, row in srcfile.iterrows():
                if 'Stadsdeel' in srcfile.columns:
                    plt.annotate(text = row['Stadsdeel'], xy=row['coords'], horizontalalignment= 'center', fontsize=12, zorder=20) 
                elif 'gm_naam' in srcfile.columns:
                    plt.annotate(text = row['gm_naam'], xy=row['coords'], horizontalalignment= 'center', fontsize=12, zorder=20)
                elif 'KOMNAVN' in srcfile.columns:
                    plt.annotate(text = row['KOMNAVN'], xy=row['coords'], horizontalalignment= 'center', fontsize=12, zorder=20)
                elif 'SOGNENAVN' in srcfile.columns:
                    plt.annotate(text = row['SOGNENAVN'], xy=row['coords'], horizontalalignment= 'center', fontsize=12, zorder=20)
                elif 'name' in srcfile.columns:
                    plt.annotate(text = row['name'], xy=row['coords'], horizontalalignment= 'center', fontsize=12, zorder=20)
                elif 'COD_Z_URB' in srcfile.columns:
                    plt.annotate(text = row['COD_Z_URB'], xy=row['coords'], horizontalalignment= 'center', fontsize=7, zorder=20)
                elif 'nazwa' in srcfile.columns:
                    plt.annotate(text = row['nazwa'], xy=row['coords'], horizontalalignment= 'center', fontsize=7, zorder=20)
                else:
                    print("There is no column for labels")

        xlim = ([srcfile.total_bounds[0],  srcfile.total_bounds[2]])
        ylim = ([srcfile.total_bounds[1],  srcfile.total_bounds[3]])
    else:
        xlim = ([src.bounds[0],  src.bounds[2]])
        ylim = ([src.bounds[1],  src.bounds[3]])
    if invertArea:
        outArea= gpd.read_file(invertArea)
        outArea.plot(ax=ax, facecolor='#FFFFFF', edgecolor='#000000', linewidth=.3, zorder=3 )
    if neighPath:
        neighborhoods = gpd.read_file(neighPath)
        neighborhoods.plot(ax=ax, facecolor='none', edgecolor='#000000', linewidth=.3, alpha=0.6, zorder=4 )
    if streetsPath:
        streets = gpd.read_file(streetsPath).to_crs('EPSG:3035')
        streets.plot(ax=ax, facecolor='none', edgecolor='#000000', linewidth=.5, alpha=0.6, zorder=10)

    if waterPath:
        waterTif = rasterio.open(waterPath)
        # colors for water layer
        cmapWater = ListedColormap(["#00000000","#7fa9b060" ])
        rasterio.plot.show(waterTif, ax=ax, cmap=cmapWater, zorder=5)
    
    # Plot the data                       
    rasterio.plot.show(waterTif, ax=ax, cmap=cmapWater, zorder=5)
    rasterio.plot.show(src, ax=ax, cmap=cmap, norm=norm, extent= [src.bounds[0],src.bounds[1], src.bounds[2], src.bounds[3]], zorder=1)               
    
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Add a title
    ax.set_title(title, color="black", fontsize=18)
    # Connect labels and colors, create legend and save the image
    patches = [mpatches.Patch(color=color, label=label)
                for color, label in legend_labels.items()]     
    if city == 'ams':
        ax.legend(handles=patches,  loc='lower left', facecolor="white", fontsize=12, title = LegendTitle, title_fontsize=14).set_zorder(6)
    elif city == 'cph':
        ax.legend(handles=patches,  loc='upper left', facecolor="white", fontsize=12, title = LegendTitle, title_fontsize=14).set_zorder(6)
    else:        
        ax.legend(handles=patches,  loc='lower right', facecolor="white", fontsize=12, title = LegendTitle, title_fontsize=14).set_zorder(6)
    print("-----PLOTTING IMAGE {}-----".format(title))
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)
    plt.savefig(exportPath, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(),transparent=True)
    
    plt.cla()
    plt.close()
