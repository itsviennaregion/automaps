#!/usr/bin/env python3

# Prepare sys.path to allow loading user config with 'import automapsconf'
import sys

conf_path, automaps_path = sys.argv[1:]
if conf_path not in sys.path:
    sys.path.insert(0, conf_path)
if automaps_path not in sys.path:
    sys.path.append(automaps_path)

from automaps.messaging.registry import Registry

if __name__ == "__main__":
    registry = Registry()
    registry.listen()
