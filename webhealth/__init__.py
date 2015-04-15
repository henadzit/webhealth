
import time
import re

import random
import requests
import gevent
from influxdb import influxdb08


HTTP_HTTPS_REGEX = re.compile('$https?://')


def _get_websites_generator(filename):
    with open(filename) as f:
        websites = (w.strip() for w in f.readlines() if not w.strip().startswith('#'))

    for w in websites:
        if HTTP_HTTPS_REGEX.match(w):
            yield w
        else:
            yield 'http://' + w


def _post_metric(website, success, load_time, code=None):
    print('M: website={}, time={}, success={}, code={}, load_time={}'.format(website, time.time(), success, code, load_time))


def _open_website(website, interval, **headers):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
    }
    default_headers.update(**headers)

    # prevents greenlets from starting pulling data all at once
    time.sleep(random.randint(0, interval))

    while True:
        start = time.time()
        try:
            resp = requests.get(website,
                                headers=headers,
                                allow_redirects=True,
                                verify=False,
                                timeout=5)
        except requests.RequestException:
            duration = time.time() - start
            _post_metric(website, False, duration)
        else:
            duration = time.time() - start
            _post_metric(website, resp.ok, duration, resp.status_code)

        sleep_time = interval - duration
        if sleep_time > 0:
            time.sleep(sleep_time)


def run(website_filename, interval=60):
    threads = []

    for website in _get_websites_generator(website_filename):
        threads.append(gevent.spawn(_open_website, website, interval))

    gevent.joinall(threads)