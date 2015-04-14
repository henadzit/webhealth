import time

import requests
from influxdb import influxdb08


def _get_websites(filename):
    with open(filename) as f:
        return [w.strip() for w in f.readlines()]


def _post_metric(website, success, load_time, code=None):
    print('M: website={}, success={}, code={}, load_time={}'.format(website, success, code, load_time))


def _open_website(website, **headers):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
    }
    default_headers.update(**headers)

    start = time.time()
    try:
        resp = requests.get(website,
                            headers=headers,
                            allow_redirects=True,
                            verify=False,
                            timeout=5)
    except requests.RequestException:
        _post_metric(website, False, time.time() - start)
        pass
    else:
        _post_metric(website, resp.ok, time.time() - start, resp.status_code    )


def run(website_filename):
    for website in _get_websites(website_filename):
        _open_website(website)