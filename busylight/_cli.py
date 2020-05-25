# _*_ coding: utf-8 _*_
"""CLI

This module is responsible for configuring and parsing the command line
arguments.
"""
import argparse
from os import getenv


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Drop the import error on the floor (╯°□°)╯︵ ┻━┻
    pass

_parser = argparse.ArgumentParser(description='An Azure IoT Busy Light Device')
_parser.add_argument(
    '--id-scope',
    type=str,
    help='The ID Scope provided by Azure',
    default=getenv('BUSY_LIGHT_ID_SCOPE')
)
_parser.add_argument(
    '--device-id',
    type=str,
    help='The Device ID provided by Azure',
    default=getenv('BUSY_LIGHT_DEVICE_ID')
)
_parser.add_argument(
    '--primary-key',
    type=str,
    help='The Primary Key provided by Azure',
    default=getenv('BUSY_LIGHT_PRIMARY_KEY')
)
_parser.add_argument(
    '-v', '--verbosity',
    action='count',
    help='increase output verbosity',
    default=0
)
args = _parser.parse_args()
