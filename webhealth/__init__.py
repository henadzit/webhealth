from __future__ import print_function

import datetime
import time
import re
import random
import sys

import requests
import gevent

from webhealth.model import Metric


HTTP_HTTPS_REGEX = re.compile('^https?://')

# only desktop browsers to catch only desktop errors. I might need to do mobile checks separately.
# It has the format (User-Agent, Accept)
COMMON_HEADERS = [
    # Chrome
    ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36',
     'application/xml,application/xhtml+xml,text/html;q=0.9, text/plain;q=0.8,image/png,*/*;q=0.5'),
    ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
     'application/xml,application/xhtml+xml,text/html;q=0.9, text/plain;q=0.8,image/png,*/*;q=0.5'),
    # Firefox
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:37.0) Gecko/20100101 Firefox/37.0',
     'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    ('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0',
     'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
    # Safari
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10',
     'application/xml,application/xhtml+xml,text/html;q=0.9, text/plain;q=0.8,image/png,*/*;q=0.5'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36',
     'application/xml,application/xhtml+xml,text/html;q=0.9, text/plain;q=0.8,image/png,*/*;q=0.5')
    # Sorry Internet Explorer
]


def _get_websites_generator(filename):
    with open(filename) as f:
        for w in f.readlines():
            w = w.strip()
            if not w.startswith('#'):
                yield w


class WebhealthWorker(gevent.Greenlet):
    def __init__(self, website, interval, data_log, info_log):
        gevent.Greenlet.__init__(self)
        self._website = website
        self._interval = interval
        self._data_log = data_log
        self._info_log = info_log

    def _post_metric(self, m):
        self._data_log.info(m.to_json())

    def _run(self):
        # prevents greenlets from starting pulling data all at once
        time.sleep(random.randint(0, self._interval))

        while True:
            start = datetime.datetime.now()

            try:
                endpoint = self._website if HTTP_HTTPS_REGEX.match(self._website) else 'http://' + self._website
                user_agent, accept = random.choice(COMMON_HEADERS)
                headers = {
                    'Accept': accept,
                    'User-Agent': user_agent,
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate'
                }

                resp = requests.get(endpoint,
                                    headers=headers,
                                    allow_redirects=True,
                                    verify=False,
                                    timeout=10)
            except requests.RequestException as e:
                if isinstance(e, requests.Timeout):
                    state = Metric.STATE_TIMEOUT
                elif isinstance(e, requests.TooManyRedirects):
                    state = Metric.STATE_TOO_MANY_REDIRECTS
                else:
                    self._info_log.info('Connection failure to {}'.format(self._website), exc_info=e)
                    state = Metric.STATE_OTHER_FAILURE

                # add handling of 'to many redirecs'

                http_code = 0
            else:
                state = Metric.STATE_OK if resp.ok else Metric.STATE_BAD_HTTP_CODE
                http_code = resp.status_code

            end = datetime.datetime.now()
            metric = Metric(self._website, state, start, end, http_code)
            self._post_metric(metric)

            duration = (end-start).total_seconds()
            self._info_log.info('Processed {}: duration={}, state={}'.format(self._website, duration, state))

            sleep_time = self._interval - duration
            if sleep_time > 0:
                time.sleep(sleep_time)


def run(website_filename, data_log, info_log, interval=60):
    workers = []

    for website in _get_websites_generator(website_filename):
        worker = WebhealthWorker(website, interval, data_log, info_log)
        worker.start()
        workers.append(worker)

    gevent.joinall(workers)