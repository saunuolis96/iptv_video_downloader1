# import requests # import get  # to make GET request
# import wget
import pathlib
from lxml import html
import requests
from bs4 import BeautifulSoup
import config


def download_cctv_video(session, url, filename,  folder_path):
    '''
    This will download from URL given the filename given, and will save to folder_path
    Folder path should be different for all cameras
    :param url:
    :param filename:
    :param folder_path:
    :return:
    '''
    pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
    p = pathlib.Path(pathlib.Path(folder_path, filename)) # if file does not exist then download it
    print('check if file already exists')
    if not p.is_file():
        print('file does not exit so lets download:')
        print(p)
        r = session.get(str(url + filename))
        with open(pathlib.Path(folder_path, filename), 'wb') as f:
            f.write(r.content)

def scrape_bs(url, session):
    '''
    Find Folders which I need search for video files
    :param url:
    :param session:
    :return:
    '''
    print('url: ')
    print(url)
    page = session.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    folders_to_visit = []
    strings_to_skip = [ ['Parent Directory/'], ['AVRecordFile.db']]
    table = soup.find('table' )
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td', {'class':'n'})
        cols = [ele.text.strip() for ele in cols ]
        if cols not in strings_to_skip:
            folders_to_visit.append([ele for ele in cols if ele])  # Get rid of empty values
            if cols is not cols: # Get rid of empty values
                data.append(cols)
    folders_to_visit2 = [x for x in folders_to_visit if x]
    # print('folders to visit:')
    # print(*folders_to_visit2, sep='\n')
    return folders_to_visit2

def get_session(url, username, password):
    '''
    Will login with CCTV camera ang save session for futher video files download
    :param url:
    :param username:
    :param password:
    :return:
    '''
    s = requests.session()
    s.auth = requests.auth.HTTPDigestAuth(username, password)
    r = s.get(url)
    assert r.status_code == 200
    return s

def iterate_camera(url, folder_path, mine_session, folders_to_visit ):
    '''
    This will iterate within folders and download all video files within folders
    It will not download the latest video file from last folder  - with idea that it is still being written by
    CCTV camera
    '''
    for month in folders_to_visit:
        whatsthere_day = scrape_bs(url + ''.join(month), mine_session)
        for day in whatsthere_day[:-1]:
            video_files = scrape_bs(url + ''.join(month) + ''.join(day), mine_session)
            for each_video in video_files:
                print('going through each video file :')
                print((url + ''.join(month) + ''.join(day),
                       ''.join(each_video),
                       pathlib.Path(folder_path, ''.join(month), ''.join(day))))
                download_cctv_video(mine_session,
                                    url + ''.join(month) + ''.join(day),
                                    ''.join(each_video),
                                    pathlib.Path(folder_path, ''.join(month), ''.join(day)))
                break
    last_month = folders_to_visit[-1:]
    last_month = ''.join(str(r) for v in last_month for r in v)
    print('last_month:')
    print(last_month)
    print('This logic is for the last days iteration only')
    day = whatsthere_day[-1:]  # find last day
    day = ''.join(str(r) for v in day for r in v)  # make a string out of list of lists
    print('this day:')
    print(day)
    print(''.join(day))
    video_files = scrape_bs(url + ''.join(last_month) + ''.join(day), mine_session)
    for each_video in video_files[:-1]:  # avoid downloading the last video file because it is still being recorded
        print('going through each video file :')
        print((url + ''.join(last_month) + ''.join(day),
               ''.join(each_video),
               pathlib.Path(folder_path, ''.join(last_month), ''.join(day))))
        download_cctv_video(mine_session,
                            url + ''.join(last_month) + ''.join(day),
                            ''.join(each_video),
                            pathlib.Path(folder_path, ''.join(last_month), ''.join(day)))
        break
print('iterate_camera end ')


if __name__ == '__main__':
    folder_path = config.folder_path
    url = config.camera_url
    print(config.username)
    print(config.password)
    mine_session = get_session(url, config.username, config.password)

    rtn_folders = scrape_bs(url, mine_session)   # ffrom here I get Yearly/monthly folder
    iterate_camera(url, folder_path, mine_session, rtn_folders)
    print('All files downloaded')

    #TODO: Need to make it save for crontab to avoid running multiple versions
    # Need to make different versions  for multithreading for multiple cameras/




