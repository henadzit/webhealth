"""
Table schema

create table if not exists webhealth_metrics.metrics (
    website varchar(256) not null,
    success tinyint not null,
    start_time double not null,
    end_time double not null,
    duration double not null,
    http_code smallint not null
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

import argparse
import getpass
import textwrap

import MySQLdb

import webhealth


INSERT_BATCH_LIMIT = 100


class MetricDAO(object):
    def __init__(self, db, user, password):
        self._db = MySQLdb.connect(host='localhost',
                                   user=user,
                                   passwd=password,
                                   db=db)
        self._buffer_to_insert = []

    def add(self, metric):
        self._buffer_to_insert.append(metric)

        if len(self._buffer_to_insert) >= INSERT_BATCH_LIMIT:
            self.flush_buffer()

    def flush_buffer(self):
        if self._buffer_to_insert:
            c = self._db.cursor()
            c.executemany(textwrap.dedent('''insert into metrics (website, success, start_time, end_time, duration, http_code)
                                             values (%s, %s, %s, %s, %s, %s)'''), [m.to_mysql_tuple() for m in self._buffer_to_insert])
            self._db.commit()

            self._buffer_to_insert = []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', dest='filename', required=True)
    parser.add_argument('--user', dest='user', required=True)
    parser.add_argument('--db-name', dest='db_name', required=True)
    args = parser.parse_args()

    metric_dao = MetricDAO(args.db_name,
                           args.user,
                           getpass.getpass())

    with open(args.filename) as f:
        for l in f.readlines():
            metric = webhealth.Metric.from_json(l)
            metric_dao.add(metric)

    metric_dao.flush_buffer()


if __name__ == '__main__':
    main()