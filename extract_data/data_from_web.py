#!/usr/bin/env python3
import requests
import sys
from bs4 import BeautifulSoup

# Base URL
URL = 'https://lehd.ces.census.gov/data'
# Local dir to save data
DATA_DIR = './data'

# TODO Expand paths map to include older versions
data_source_paths = {
    'lodes': 'lodes/LODES7',
    'j2j': 'j2j/latest_release',
    'qwi': 'qwi/latest_release'
}

# Rate limit client to not crash server, in effect finding the most number of data files
# in MAX_REQUESTS number of requests
MAX_REQUESTS = 1
curr_requests = 0

try:
    data_file_collector = []
    if len(sys.argv) != 2:
        raise Exception('usage')
    elif sys.argv[1] == 'all':
        # Retrieve all supported data sources
        print('Retrieving all data is not yet supported. Please specify a data source.')
    else:
        # Validate source name, get data if source is valid
        if sys.argv[1] in data_source_paths:
            URL = URL + '/' + data_source_paths[sys.argv[1]] + '/'

            # Recurse down path to find all csv files with data
            def get_csv_data(URL):
                global curr_requests
                resp = requests.get(url = URL)
                soup = BeautifulSoup(resp.content, features='html.parser')
                for link in soup.findAll('a'):
                    # Validate path is unique and not visited already
                    curr_link = link.get('href')
                    if (curr_link not in URL) and ('/' in curr_link) and (curr_requests < MAX_REQUESTS):
                        curr_requests += 1
                        get_csv_data(URL + curr_link)
                    elif 'csv' in curr_link:
                        data_file_collector.append(URL + curr_link)
            get_csv_data(URL)
            print('ATTEMPTING TO DOWNLOAD:')
            print(data_file_collector)

            for url in data_file_collector:
                file_resp = requests.get(url)
                if file_resp.status_code == 200:
                    print('Saving file from {:s} to directory {:s}'.format(url, DATA_DIR))
                    fs = open(DATA_DIR + '/' + url.split('/')[-1], 'wb')
                    fs.write(file_resp.content)
                    fs.close()
                else:
                    print('Error downloading {:s}\nReceived non-200 status code.'.format(url))

        else:
            raise Exception('unsupported')

# Handle exceptions
except Exception as e:
    err = 'Unknown error'
    if str(e) == 'usage':
        err = 'Unknown usage error\nUsage: data_from_web.py <source name>'
        if len(sys.argv) > 2:
            err = 'Too many args'
        elif len(sys.argv) < 2:
            err = 'No data source name provided'
    elif str(e) == 'unsupported':
        err = 'Unsupported data source selected'

    print('Error: {:s}\nCaused by: {:s}'.format(err, str(e)))