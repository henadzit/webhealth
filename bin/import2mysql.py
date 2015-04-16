"""
Table schema

create table if not exists webhealth_metrics.metrics (
    website varchar(256) not null,
    time double not null,
    success tinyint not null,
    code smallint not null,
    load_time double not null
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""

import argparse
import re
import getpass
import textwrap

import MySQLdb


METRIC_REGEX = re.compile('^M: website=([^,]+), time=([^,]+), success=([^,]+), code=([^,]+), load_time=([^,\n]+)$')
INSERT_BATCH_LIMIT = 100

db = None
to_insert = []


def _put_into_db(website, time, success, code, load_time):
    global to_insert
    global db

    to_insert.append((website,
                      time,
                      1 if success else 0,
                      0 if code is None or code == 'None' else code,
                      load_time))

    if len(to_insert) >= INSERT_BATCH_LIMIT:
        c = db.cursor()
        c.executemany(textwrap.dedent('''insert into metrics (website, time, success, code, load_time)
                                         values (%s, %s, %s, %s, %s)'''), to_insert)
        db.commit()

        to_insert = []


def main():
    global db
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', dest='filename', required=True)
    parser.add_argument('--user', dest='user', required=True)
    parser.add_argument('--db-name', dest='db_name', required=True)
    args = parser.parse_args()

    db = MySQLdb.connect(host='localhost',
                         user=args.user,
                         passwd=getpass.getpass(),
                         db=args.db_name)

    with open(args.filename) as f:
        for l in f.readlines():
            _put_into_db(*METRIC_REGEX.match(l).groups())


if __name__ == '__main__':
    main()