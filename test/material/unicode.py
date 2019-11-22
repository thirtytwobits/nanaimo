#!/usr/bin/env python3

import sys

if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf_16_be') as unicode_file:
        sys.stdout.write(unicode_file.read())
