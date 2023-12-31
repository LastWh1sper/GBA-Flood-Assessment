import os
import pandas as pd
import rasterio 
import numpy as np
import datetime
def readAllDepth(city,path,landuse,dt):
    print("Reading data~")
    filelist = os.listdir(path)
    wdfiles = [adata for adata in filelist if adata.endswith('.wd')]
    wdfiles.sort(reverse=True)
    
    currentpath = os.getcwd()
    # Read Pop data
    pop = rasterio.open(os.path.join(currentpath ,'data','pop','pop.tif'))
    # Read landuse data
    landuse = rasterio.open(os.path.join(currentpath ,'data', 'landuse',landuse))

    popdata = pop.read(1)
    landdata = landuse.read(1)

    poptrans = pop.transform
    landusetrans = landuse.transform

    # traffictotal = np.count_nonzero(landdata == 1) * landuse.res[0]**2
    # bdtotal = np.count_nonzero(landdata == 6) * landuse.res[0]**2
    # croptotal = np.count_nonzero(landdata == 5) * landuse.res[0]**2
    # allarea = np.count_nonzero((landdata > 0 ) & (landdata < 13)) * landuse.res[0]**2

    condition = lambda x: x == 1
    traffictotal = count_elements(landdata, condition) * landuse.res[0]**2
    print("Traffic Area: {} km^2".format(traffictotal/1000/1000))
    condition = lambda x: x == 6
    bdtotal = count_elements(landdata, condition) * landuse.res[0]**2
    print("Building Area: {} km^2".format(bdtotal/1000/1000))
    condition = lambda x: x == 5
    croptotal = count_elements(landdata, condition) * landuse.res[0]**2
    print("Crop Area: {} km^2".format(croptotal/1000/1000))
    condition = lambda x: (x > 0 ) & (x < 13)
    allarea = count_elements(landdata, condition) * landuse.res[0]**2
    print("Total Area: {} km^2".format(allarea/1000/1000))
    

    
       
    colname =['时间', '轻度积水面积', '中度积水面积', '重度积水面积', '轻度积水比例', '中度积水比例', '重度积水比例',
               '体积', '作物受损面积', '作物受损比例', '建筑受损面积', '建筑受损比例', '交通受损面积', '交通受损比例', '影响人口']
    df = pd.DataFrame(columns= colname)
    
    for wdfile in wdfiles:
        wdpath = os.path.join(path, wdfile)
        name = wdfile.split('-')
        name = name[1].split('.')
        if np.mod(int(name[0]), 3) ==0:
            ctime = int( name[0]) * dt
            ttime = str(datetime.timedelta(seconds=ctime))
            print("Processing {} Time = {} ".format(city, ctime))

            qingA = 0.0
            zA = 0.0
            zhongA = 0.0
            volume = 0.0
            cropA = 0.0
            bdA = 0.0
            trafficA = 0.0
            affectedPeople = 0.0
            with rasterio.open(wdpath) as src:
                # Read the raster data
                ddata = src.read(1)
                area = src.res[0]**2
                # Get the metadata of the raster
                profile = src.profile
                # Get the affine transformation matrix
                transform = src.transform
                # Get the number of rows and columns in the raster
                rows, cols = ddata.shape
                # Loop through each cell in the raster
                #@par(schedule='dynamic', chunk_size=100, num_threads=4)
                for row in range(rows):
                    for col in range(cols):
                        # Get the value of the cell
                        depthvalue = ddata[row, col] 
                        # Convert the row and column indices to coordinates
                        x, y = transform * (col, row)
                        # read  population greater than 1cm should be count
                        if depthvalue > 0.01:
                            landtype = readRasterValue(x, y, landuse,landusetrans)
                            popdensity = readRasterValue(x, y, pop, poptrans)
                            #water body NotCount
                            if landtype != 10 and landtype != 9:
                                volume  += area*depthvalue                      
                                if depthvalue < 0.15:
                                    qingA += area
                                elif depthvalue < 0.4:
                                    zA  += area
                                    if(landtype) == 1:
                                        trafficA += area
                                    elif(landtype) == 5:
                                        cropA += area
                                    elif(landtype) == 6: 
                                        bdA += area
                                    affectedPeople += popdensity / 10000 * area
                                else:
                                    zhongA += area
                                    if(landtype) == 1:
                                        trafficA += area
                                    elif(landtype) == 5:
                                        cropA += area
                                    elif(landtype) == 6:
                                        bdA += area 
                                    affectedPeople += popdensity / 10000 * area
                            #count landusetype 
                # Preapare data
                output1 = [ttime,qingA,zA,zhongA, qingA/allarea, zA/allarea, zhongA/allarea, volume, cropA, cropA / croptotal, bdA, bdA/bdtotal, trafficA, trafficA/traffictotal, affectedPeople]
                data1 = pd.Series(output1, index = df.columns)
                print(data1)
                df.loc[len(df)] = data1
            
    df.to_csv(city+'.csv')
    return

def readRasterValue(x, y, src, trans):
    col, row = ~trans * (x, y)
    value = src.read(1, window=((row, row+1), (col, col+1)))
    return value[0][0]


def count_elements1(array, condition):
    count = 0
    # 使用NumPy的迭代器遍历数组的所有元素
    for element in np.nditer(array):
        # 判断元素是否符合条件
        if condition(element):
            count += 1
    return count

def count_elements(array, condition):
    # 将数组分为10份
    sub_arrays = np.array_split(array, 40)
    counts = []
    # 统计每份数据中符合条件的数量
    for ii, sub_array in enumerate(sub_arrays):
        print("COUNT ITEM : {}".format(ii))
        counts.append(np.count_nonzero(condition(sub_array)))
    count = sum(counts)
    return count