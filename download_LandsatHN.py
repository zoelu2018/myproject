import landsatxplore.api
from landsatxplore.earthexplorer import EarthExplorer

def request_Landsat(username,password,product,lat,lon,start_date,end_date,cloud_max):

    api = landsatxplore.api.API(username, password)

    scenes = api.search(
        dataset=product,
        latitude=lat,
        longitude=lon,
        start_date=start_date,
        end_date=end_date,
        max_cloud_cover=cloud_max)

    print('{} scenes found.'.format(len(scenes)))
    api.logout()
    return scenes

def download_landsat(username,password,Landsat_name,output_dir):

    Earth_Down = EarthExplorer(username, password)

    for scene in Landsat_name:

        ID = scene['entityId']
        print('Downloading data %s '% ID)
        IDpro = ID[3:9]
        print(IDpro)
        # if (IDpro == "143029") or (IDpro == "143030") or (IDpro == "142030"):

        Earth_Down.download(scene_id=ID, output_dir=output_dir)

    Earth_Down.logout()

if __name__ == '__main__':

    username = 'luguozhenghpu@163.com'
    password = 'luGUOzheng123'
    product = 'LANDSAT_8_C1'
    lat = 33.1703
    lon = 111.5189
    start_date='2019-04-01'
    end_date='2019-05-31'
    cloud_max = 30
    output_dir = '/data/lgz/data'
    Landsat_name = request_Landsat(username,password,product,lat,lon,start_date,end_date,cloud_max)
    download_landsat(username,password,Landsat_name,output_dir)# cd /data/lgz/SentinelDownloadData