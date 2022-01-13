import json
import os
import os.path as path
import urllib.request
import time


def is_file_older_than_x_days(file, days=1):
    file_time = path.getmtime(file)
    # Check against 24 hours
    return (time.time() - file_time) / 3600 > 24 * days


def download_from_remote(remote_url, local_file):
    """ download from remote_url and save to local_file """

    response = urllib.request.urlopen(remote_url)

    if response.status == 200:
        resource = response.read()

        os.makedirs(path.dirname(local_file), exist_ok=True)
        with open(local_file, "wb") as file:
            file.write(resource)

        print("Downloaded file from remote "+remote_url)

    return local_file


def get_json_file(local_file, remote_url, days=1):
    if not os.path.isfile(local_file) or is_file_older_than_x_days(local_file, days):
        print("Download file because is older than 1 day")
        local_file = download_from_remote(remote_url, local_file)

    sch = open(local_file)
    return json.load(sch)
