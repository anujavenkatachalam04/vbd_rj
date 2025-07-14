

import pandas as pd
import json
import os
import tempfile
import re
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

# --- Load Google Drive credentials and file ---
def load_drive(gdrive_secrets):
    creds_dict = dict(gdrive_secrets)  # Convert to real dict
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
        json.dump(creds_dict, tmp)
        tmp.flush()
        gauth = GoogleAuth()
        gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            tmp.name,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        drive = GoogleDrive(gauth)
    return drive

# --- Sort district names ---
def get_sorted_districts(df):
    individual_districts = [d for d in df['dtname_disp'].unique() if d.lower() != 'all']
    def sort_key(name):
        match = re.search(r'\(High - (\d+)\)', name)
        if match:
            return (0, int(match.group(1)))
        else:
            return (1, name.lower())
    sorted_districts = sorted(individual_districts, key=sort_key)
    return ['All'] + sorted_districts
