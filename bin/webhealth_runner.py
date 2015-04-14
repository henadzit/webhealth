
import argparse

import webhealth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--website-file', dest='website_file', required=True)
    args = parser.parse_args()

    webhealth.run(args.website_file)


if __name__ == '__main__':
    main()