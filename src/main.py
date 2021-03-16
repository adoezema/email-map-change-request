import logging
import yaml
from arcgis.gis import GIS, Item
from yaml.loader import SafeLoader
from pathlib import Path
from typing import List
from rich.logging import RichHandler

logging.basicConfig(level="INFO", format='%(asctime)s - [%(levelname)s] - %(message)s',
                        datefmt='[%X]', handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger('rich')

def login(username, password) -> GIS:
    gis: GIS = GIS(username=username, password=password)
    return gis

def search_content(gis, wild_card_title, item_type='Feature Service') -> List[Item]:
    query = "title:" + wild_card_title
    result = gis.content.search(query=query, item_type=item_type)
    if result:
        return result
    else:
        log.warning(f'No Match found')

if __name__ == "__main__":
    parent = Path(r'C:\Users\adoezema\PycharmProjects\ArcGIS_Online_Admin\email-map-change-request')
    file_loc = r'settings\account_info.yaml'
    with open(Path(parent, file_loc)) as file:
        accounts = yaml.load(file, Loader=yaml.SafeLoader)
        for org, info in accounts.items():
            try:
                gis = login(info['user'], info['password'])
                log.info(f'[ACCESS ACCOUNT] Logged into {org} as: {gis.users.me.username}')
                content = search_content(gis, '*Map Change Request*')
                if content:
                    log.info(f'[SEARCH] Found {content}')

            except Exception as e:
                log.exception(e)
    