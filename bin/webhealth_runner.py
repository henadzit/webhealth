from gevent import monkey
monkey.patch_all()

import argparse

import webhealth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--website-file', dest='website_file', required=True)
    parser.add_argument('--interval', dest='interval', default=60)
    args = parser.parse_args()

    webhealth.run(args.website_file)


if __name__ == '__main__':
    main()