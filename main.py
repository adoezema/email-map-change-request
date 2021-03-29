import logging
import pandas as pd
import yaml
from arcgis.gis import GIS, Item
from arcgis.features import FeatureLayer, FeatureLayerCollection
from datetime import datetime
from yaml.loader import SafeLoader
from pathlib import Path
from typing import List, Dict
from rich.logging import RichHandler
from email_users import email_report
from settings import email_participants

#TODO: Add Type Hints and Docstrings

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
        log.warning(f'No Map Change Request Feature Service found')
        
def find_open_issues(agol_item) -> List[Dict]:
    results = []
    feat_lyr_col: FeatureLayerCollection = FeatureLayerCollection.fromitem(agol_item)
    field_mapping = {'Update_Status': 'New',
                        'STATUS': 'Open'}
    for feat_lyr in feat_lyr_col.layers:
        log.info(f'Item: {agol_item.title} Layer: {feat_lyr}')
        field_names = [fld.name for fld in feat_lyr.properties.fields]
        log.debug([fld.name for fld in feat_lyr.properties.fields])
        if not any(fld in field_names for fld in field_mapping.keys()):
            raise Exception(f'Fields {field_mapping.keys()} not found in {agol_item.title} - Layer: {feat_lyr.properties.name}')
        for name, status in field_mapping.items():
            try:           
                count = feat_lyr.query(where=f"{name}='{status}'", return_count_only=True)
                log.info(f'[QUERY] - {count} Open Issues')
                results.append({'Feature Service': agol_item.title, 'Layer': feat_lyr.properties.name, 'Count': count})
            except Exception:
                log.warning(f'Field: {name} not in {feat_lyr.properties.name}')
    return results

def convert_to_df(data) -> pd.DataFrame:
    result = pd.DataFrame()
    for community in data:
        name = list(community.keys())[0]
        #TODO: Log empty DataFrame Communities?
        community_df = pd.DataFrame(community[name])
        community_df['Community Name'] = name
        result = result.append(community_df, ignore_index=True)
    
    return result


if __name__ == "__main__":
    workspace = Path(__file__).resolve().parents[0]
    open_map_change_requests = []
    with open(Path.joinpath(workspace, 'settings', 'account_info.yaml')) as file:
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
    log.info(open_map_change_requests)
    
    data_df = convert_to_df(open_map_change_requests)
    html_tbl = data_df.to_html()
    data_dir = Path.joinpath(workspace, 'data').absolute()
    log.info(f'[FILE] Creating new excel table in {data_dir}')
    excel_tbl = Path.joinpath(data_dir,f"c{datetime.now().strftime('%Y%m%d')}_Open_Map_Change_Requests.xlsx")
    data_df.to_excel(excel_tbl)

    email_report(email_participants.users, html_tbl, str(excel_tbl), len(accounts))