

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
        # High Districts
        match_high = re.search(r'\(High District - (\d+)\)', name)
        if match_high:
            return (0, int(match_high.group(1)))

        # Districts with High Blocks
        elif "(Has High Blocks)" in name:
            return (1, name.lower())

        # Other districts
        else:
            return (2, name.lower())

    sorted_districts = sorted(individual_districts, key=sort_key)
    return ['All'] + sorted_districts

# --- Sort subdistrict names ---
def get_sorted_subdistricts(df):
    individual_subdistricts = [sd for sd in df['sdtname_disp'].unique() if sd.lower() != 'all']
    def sort_key(name):
        match = re.search(r'\(High Block - (\d+)\)', name)
        if match:
            return (0, int(match.group(1)))
        else:
            return (1, name.lower())
    sorted_subdistricts = sorted(individual_subdistricts, key=sort_key)
    return ['All'] + sorted_subdistricts
