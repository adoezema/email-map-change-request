import logging
import yaml
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer, FeatureLayerCollection
from yaml.loader import SafeLoader
from pathlib import Path
from typing import List, Dict
from rich.logging import RichHandler


logging.basicConfig(level="INFO", format='%(asctime)s - %(message)s',
                        datefmt='[%X]', handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger('rich')

def login(username, password) -> GIS:
    gis: GIS = GIS(username=username, password=password)
    return gis

def search_content(gis, wild_card_title, item_type='Feature Service') -> List[Item]:
    query = "title:" + wild_card_title
    result = gis.content.search(query=query, item_type=item_type)
    if result:
        return [i for i in result if i.content_status != 'deprecated']
    else:
        log.warning(f'No Match found')
        
def find_open_issues(agol_item) -> List[Dict]:
    results = []
    feat_lyr_col: FeatureLayerCollection = FeatureLayerCollection.fromitem(agol_item)
    field_mapping = {'Update_Status': 'New',
                        'STATUS': 'Open'}
    for feat_lyr in feat_lyr_col.layers:
        log.info(f'Layer: {feat_lyr}')
        log.debug([fld.name for fld in feat_lyr.properties.fields])
        for name, status in field_mapping.items():
            try:           
                count = feat_lyr.query(where=f"{name}='{status}'", return_count_only=True)
                log.info(f'[QUERY] - {count} Open Issues')
                results.append({'Layer': feat_lyr.properties.name, 'Count': count})
            except Exception:
                log.warning(f'Field: {name} not in {feat_lyr.properties.name}')
    return results

if __name__ == "__main__":
    parent = Path(r'C:\Users\adoezema\PycharmProjects\ArcGIS_Online_Admin\email-map-change-request')
    file_loc = r'settings\account_info.yaml'
    open_map_change_requests = []
    with open(Path(parent, file_loc)) as file:
        accounts = yaml.load(file, Loader=yaml.SafeLoader)
        for org, info in accounts.items():
            try:
                gis = login(info['user'], info['password'])
                log.info(f'[ACCESS ACCOUNT] Logged into {org} as: {gis.users.me.username}')
                content = search_content(gis, '*Map Change Request*')
                if content:
                    log.info(f'[SEARCH] Found {content}')
                    for item in content:
                        open_issues = find_open_issues(item)
                        open_map_change_requests.append({org: open_issues})
            except Exception as e:
                log.exception(e)
        print(open_map_change_requests)
    