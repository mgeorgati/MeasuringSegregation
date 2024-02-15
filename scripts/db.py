import psycopg2
from sqlalchemy import create_engine
import geopandas as gpd
import time
from config.config import gdal_rasterize_path
from config.rom import raster_file
# connection establishment
conn = psycopg2.connect(
   database="myinnrer_db", #myinnrer_db
    user='postgres',
    password='postgres',
    host='localhost',
    port= ''
)

pghost = 'localhost'
pgport = '5432'
pguser = 'postgres'
pgpassword = 'postgres'
pgdatabase = "myinnrer_db"
conn.autocommit = True
cur = conn.cursor()
engine = create_engine(f'postgresql://{pguser}:{pgpassword}@{pghost}:{pgport}/{pgdatabase}?')

import subprocess
from osgeo import gdal
def shptoraster(raster_file, src_file, gdal_rasterize_path, dst_file, column_name, xres=100, yres=100):
    '''
    Takes the path of GeoDataframe and converts it to raster
        raster_file         : str
            path to base raster, from which the extent of the new raster is calculated 
        src_file            : str
            path to source file (SHP,GEOJSON, GPKG) 
        gdal_rasterize_path : str
            path to execute gdal_rasterize.exe
        dst_file            : str
            path and name of the destination file
        column_name         : str
            Field to use for rasterizing
    '''
    data = gdal.Open(raster_file)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None    
    cmd = """gdal_rasterize -a "{9}" -te {1} {2} {3} {4} -tr {5} {6} "{7}" "{8}" """\
                .format(gdal_rasterize_path, minx, miny, maxx, maxy, xres, yres, src_file, dst_file, column_name)
                
    print(cmd)
    subprocess.call(cmd, shell=True)
    
import geopandas as gpd    
def dbTOraster(city, gdal_rasterize_path, engine, raster_file, temp_shp_path, temp_tif_path, column_name, layerName, attr_value, year):
    # Create SQL Query
    sql = """SELECT "FID", "{0}", geometry FROM {1}_arealweight""".format(column_name, city) #geom
    # Read the data with Geopandas
    gdf = gpd.GeoDataFrame.from_postgis(sql, engine, geom_col='geometry' ) #geom 

    # exporting water cover from postgres
    print("Exporting {0} from postgres".format(column_name))
    src_file = temp_shp_path + "/{0}_{1}Grid.geojson".format(attr_value, year)
    gdf.to_file(src_file,  driver="GeoJSON")   
    dst_file = temp_tif_path + "/{0}.tif".format(layerName)
    
    shptoraster(raster_file, src_file, gdal_rasterize_path, dst_file, column_name, xres=100, yres=100)
import csv
def saveDB(cur , conn,city):
    # execute a sql query
    cur.execute("SELECT * FROM {0}_arealweight".format(city))

    # fetch the results
    results = cur.fetchall()

    # open a file in the downloads folder
    with open("/home/ubuntu/MeasuringSegregation/Rome/data/db_wa.csv", "w", newline="") as f:
        # Create a CSV writer
        writer = csv.writer(f)

        # write the column names
        writer.writerow([col[0] for col in cur.description])

        # write the query results
        writer.writerows(results)

    # close the cursor and connection
    cur.close()
    conn.close()

def deleteDB(cur,conn,city):
    # drop table accounts
    sql = "DROP TABLE {0}_arealweight".format(city)
    
    # Executing the query
    cur.execute(sql)
    print("Table dropped !")
    
    # Commit your changes in the database
    conn.commit()
    
    # Closing the connection
    conn.close()

def importTables(year, conn,cur):
    

    src_file = "/home/ubuntu/MeasuringSegregation/Rome/data/censusTracts/{}_rom.gpkg".format(year)
    df = gpd.read_file(src_file)
    df.to_postgis('rom_{0}_censustracts'.format(year),engine)
    print('Sucessfully in')

def calculateArealWeights(city,year, attr_value, conn,cur):
    factor = "{0}_{1}".format(attr_value, year)

    print("Set Coordinate system for GRID")
    cur.execute("SELECT UpdateGeometrySRID('{0}_grid','geometry',3035);;".format(city))  # 4.3 sec
    conn.commit()

    #-------------------------------------------------------------------------------------------------------------------
    print("Checking {0} cover analysis table".format(city))
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'public' AND tablename = '{0}_arealweight');".format(
            city))
    check = cur.fetchone()
    if check[0] == False:
        print("Creating {0} cover analysis table".format(city))
        # Watercover percentage:
        cur.execute("Create table {0}_arealweight as \
                            (SELECT * \
                            FROM {0}_grid);".format(city))  # 4.3 sec
        conn.commit()
    else:
        print("{0} cover analysis table already exists".format(city))
    #-------------------------------------------------------------------------------------------------------------------

    print("Set Coordinate system for cover analysis")
    cur.execute("SELECT UpdateGeometrySRID('{0}_arealweight','geometry',3035);;".format(city))  # 4.3 sec
    conn.commit()

    # Adding necessary columns to city cover analysis table ---------------------------------------------------------
    print("---------- Adding necessary column to {0}_arealweight table, if they don't exist ----------".format(city))

    print("Checking {0} cover analysis - {1} column".format(city,factor))
    cur.execute("""SELECT EXISTS (SELECT 1 \
                FROM information_schema.columns \
                WHERE table_schema='public' AND table_name='{0}_arealweight' AND column_name='{1}_{2}_coverage');""".format(city,attr_value,year))
    
    check = cur.fetchone()
    print(check[0])
    if check[0] == False:
        print("Creating {0} cover analysis - {1} column".format(city,factor))
        # Adding water cover column to cover analysis table
        cur.execute(
            """Alter table {0}_arealweight \
            ADD column "{1}_{2}_coverage" double precision default 0;""".format(city,attr_value,year))  # 11.3 sec #, \add column id SERIAL PRIMARY KEY
        conn.commit()
    else:
        print("{0} cover analysis - {1} column already exists".format(city,factor))
    
    print("---------- Calculating {0} cover percentage ----------".format(factor))
    # start total query time timer
    start_query_time = time.time()

    # getting id number of chunks within the iteration grid covering the city ---------------------------------------
    ids = []
    cur.execute("""SELECT csid FROM rom_{0}_censustracts WHERE rom_{0}_censustracts."{1}">0;""".format(year, attr_value))
    chunk_id = cur.fetchall()

    # saving ids to list
    for id in chunk_id:
        ids.append(id[0])
    
    print(len(ids))
    print("""WITH f AS ( SELECT rom_{1}_censustracts."{0}" as pop , a."FID" as id, 
                st_area(rom_{1}_censustracts.geometry) as totalArea, rom_{1}_censustracts.csid,
		   ST_AREA(ST_INTERSECTION(rom_{1}_censustracts.geometry, a.geometry)) as x_area 
		   FROM rom_grid a, rom_{1}_censustracts  
		   where rom_{1}_censustracts."{0}" > 0 and ST_INTERSECTS(rom_{1}_censustracts.geometry, a.geometry) )     
            UPDATE rom_arealweight SET "{2}_coverage" =  CASE \
                WHEN rom_arealweight."{2}_coverage"= 0 THEN ROUND(f.pop* f.x_area/f.totalArea ::NUMERIC,2) \
                ELSE rom_arealweight."{2}_coverage"= (rom_arealweight."{2}_coverage" + f.pop* f.x_area/f.totalArea) ::NUMERIC,2) \
                from f where f.id= rom_arealweight."FID";""".format(attr_value,year,factor))
    for census in ids:
        cur.execute("""WITH f AS ( SELECT rom_{1}_censustracts."{0}" as pop , a."FID" as id, 
                    st_area(ST_MakeValid(rom_{1}_censustracts.geometry)) as totalArea, rom_{1}_censustracts.csid,
            ST_AREA(ST_INTERSECTION(ST_MakeValid(rom_{1}_censustracts.geometry), a.geometry)) as x_area 
            FROM rom_grid a, rom_{1}_censustracts  
            where rom_{1}_censustracts.csid={3} AND ST_INTERSECTS(ST_MakeValid(rom_{1}_censustracts.geometry), a.geometry) )     
                UPDATE rom_arealweight SET "{2}_coverage" =  CASE \
                    WHEN rom_arealweight."{2}_coverage"= 0 THEN f.pop * f.x_area/f.totalArea \
                    WHEN rom_arealweight."{2}_coverage">0 THEN (rom_arealweight."{2}_coverage" + (f.pop* f.x_area/f.totalArea))
                    END\
                    from f where f.id= rom_arealweight."FID";""".format(attr_value,year,factor, census))  # 1.6 sec
        conn.commit()
    
    # stop total query time timer
    stop_query_time = time.time()

    # calculate total query time in minutes
    total_query_time = (stop_query_time - start_query_time) / 60
    print("Total {1} cover query time : {0} minutes".format(total_query_time,factor))

   
city = 'rom'
#saveDB(cur , conn, city) 
deleteDB(cur,conn,city)
#src_file1 = "/home/ubuntu/MeasuringSegregation/Rome/data/censusTracts/rom_grid.geojson"
#df1 = gpd.read_file(src_file1)
#df1.to_postgis('rom_grid',engine)
print('grid successfully imported')
attr_values = [ 'totalpop']  #'BGD', 'PHL', 'ROU', 'EU', 'nonEUEu', 'Africa' ,'America', 'Asia', 'totalpop', 'totalmig', 'ITA'
years_list= [2020 ]#, 2015, 2016, 2017, 2018, 2019, 2020 ]
for year in years_list:  
    #importTables(year,  conn,cur)
    #print('Table {0} successfully imported'.format(year))
    for attr_value in attr_values:
        #print('')
        #calculateArealWeights('rom', year, attr_value, conn, cur)#, engine)
        temp_shp_path = "/home/ubuntu/MeasuringSegregation/Rome/data/SHP_AW/"
        temp_tif_path = "/home/ubuntu/MeasuringSegregation/Rome/data/GeoTIFF_AW/"
        #dbTOraster(city, gdal_rasterize_path, engine, raster_file, temp_shp_path, temp_tif_path, "{0}_{1}_coverage".format(attr_value, year), "{0}_{1}".format(year,attr_value), attr_value, year)
    print('Table {0} successfully processed'.format(year))

