#!/usr/bin/env python3

import time

from networktables import NetworkTables


def main():
    NetworkTables.initialize()
    entry = NetworkTables.getEntry('/vision/info')
    entry.addListener(hook, NetworkTables.NotifyFlags.NEW | NetworkTables.NotifyFlags.UPDATE)

    time.sleep(60)


def hook(entry, key, value, param):
    print(time.monotonic(), *value, sep=',')


if __name__ == "__main__":
    main()
