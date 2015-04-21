from __future__ import print_function

import time
import re
import random
import sys

import requests
import gevent
import jsonpickle


HTTP_HTTPS_REGEX = re.compile('^https?://')


class Metric(object):
    def __init__(self, website, success, start_time, end_time, http_code, exception=None):
        self.website = website
        self.success = success
        self.start_time = start_time
        self.end_time = end_time
        self.http_code = http_code
        self.exception = exception

    def to_json(self):
        return jsonpickle.encode(self)

    def to_mysql_tuple(self):
        return (self.website,
                1 if self.success else 0,
                self.start_time,
                self.end_time,
                self.end_time - self.start_time, # duration
                0 if self.http_code is None else self.http_code)


    @staticmethod
    def from_json(json_str):
        return jsonpickle.decode(json_str)


def _get_websites_generator(filename):
    with open(filename) as f:
        websites = (w.strip() for w in f.readlines() if not w.strip().startswith('#'))

    for w in websites:
        if HTTP_HTTPS_REGEX.match(w):
            yield w
        else:
            yield 'http://' + w


def _post_metric(metric):
    print(metric.to_json())


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
        except requests.RequestException as e:
            end = time.time()
            metric = Metric(website, False, start, end, None, e)
            _post_metric(metric)
        else:
            end = time.time()
            metric = Metric(website, resp.ok, start, end, resp.status_code)
            _post_metric(metric)
        print('trace: {}: duration={}s'.format(website, end-start), file=sys.stderr)

        sleep_time = interval - (end - start)
        if sleep_time > 0:
            time.sleep(sleep_time)


def run(website_filename, interval=60):
    threads = []

    for website in _get_websites_generator(website_filename):
        threads.append(gevent.spawn(_open_website, website, interval))

    gevent.joinall(threads)