from gevent import monkey
monkey.patch_all()

import argparse
import logging
import logging.handlers
import socket
import os

import webhealth


APP_NAME = 'webhealth'


def _get_data_logger(output_dir):
    data_logger = logging.getLogger('{}_data'.format(APP_NAME))
    data_logger.setLevel(logging.INFO)

    # rotate every three hours
    fh = logging.handlers.TimedRotatingFileHandler(os.path.join(output_dir, '{}.metrics'.format(APP_NAME)),
                                                   when='H', interval=3)
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    data_logger.addHandler(fh)

    return data_logger


def _get_info_logger(output_dir):
    info_logger = logging.getLogger(APP_NAME)
    info_logger.setLevel(logging.INFO)

    # rotate every day
    fh = logging.handlers.TimedRotatingFileHandler(os.path.join(output_dir, '{}.log'.format(APP_NAME)),
                                                   when='D', interval=1)
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    info_logger.addHandler(fh)

    return info_logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--website-file', dest='website_file', required=True)
    parser.add_argument('--interval', dest='interval', default=60)
    parser.add_argument('--output-dir', dest='output_dir', default=os.getcwd())
    args = parser.parse_args()

    webhealth.run(socket.gethostname(),
                  args.website_file,
                  _get_data_logger(args.output_dir),
                  _get_info_logger(args.output_dir),
                  args.interval)


if __name__ == '__main__':
    main()