#!/usr/bin/env python3
import sys
from occulis_server.power_control import PowerController

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: cycle_relay.py <rig_name>')
        sys.exit(1)
    pc = PowerController('config/rigs.yaml')
    if not pc.trigger_relay(sys.argv[1]):
        print('Unknown rig')
