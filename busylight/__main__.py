# _*_ coding: utf-8 _*_
"""Azure IoT Busy Light

This application integrates with Azure IoT Central and Azure Logic Apps to run
different routines when a command is sent to the device via Azure IoT Central.
"""
import asyncio
import logging
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse
from gpiozero import LED

from ._cli import args
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

logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')
_logger = logging.getLogger(__name__)

if args.verbosity == 0:
    _logger.setLevel(logging.ERROR)
elif args.verbosity == 1:
    _logger.setLevel(logging.WARN)
elif args.verbosity == 2:
    _logger.setLevel(logging.INFO)
elif args.verbosity >= 3:
    _logger.setLevel(logging.DEBUG)
    if args.verbosity > 3:
        _logger.debug('Whoa... I can\'t be that verbose')

_outputs = {
    'red': LED(6),
    'yellow': LED(13),
    'green': LED(19),
    'buzzer': LED(26)
}

_request_handlers = {
    'Busy': lambda: (
        _outputs['red'].on(),
        _outputs['buzzer'].blink(n=3)
    ),
    'Warn': _outputs['yellow'].on,
    'Free': _outputs['green'].on,
}

# Clear all _outputs

def _clear__outputs():
    """Clears all output pins
    """
    for led in _outputs.values():
        led.off()

async def main():
    """
    Runs the IoT device's event loop.

    Returns None
    """
    device_client = None
    try:
        _logger.debug('Attempting to create a provisioning device client')
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host='global.azure-devices-provisioning.net',
            registration_id=args.device_id,
            id_scope=args.id_scope,
            symmetric_key=args.primary_key,
        )
        _logger.info('Successfully created a provisioning device client')

        _logger.debug('Attempting to register provisioning device client')
        registration_result = await provisioning_device_client.register()
        _logger.info('Successfully registered provisioning device client')

        # build the connection string
        conn_str = 'HostName=' + registration_result.registration_state.assigned_hub + \
                    ';DeviceId=' + args.device_id + \
                    ';SharedAccessKey=' + args.primary_key

        # The client object is used to interact with your Azure IoT Central.
        device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

        _logger.info('Connecting...')
        await device_client.connect()
        _logger.info('Connected')

        # Get the current routine
        twin = await device_client.get_twin()
        _logger.debug('Got twin: %s', twin)

        routine = None
        try:
            routine = twin['reported']['routine']
            _logger.debug('Previous routine was %s', routine)
        except KeyError:
            _logger.warning('No previously reported routine found')

        if routine is not None and routine in _request_handlers:
            _request_handlers[routine]()

        while True:
            method_request = await device_client.receive_method_request()
            _logger.debug('Handling method: %s', method_request.name)
            _clear__outputs()
            result = True
            status = 200
            if method_request.name in _request_handlers.keys():
                _logger.debug('Running %s task', method_request.name)
                _request_handlers[method_request.name]()
            else:
                _logger.error('Unknown method: %s', method_request.name)
                result = False
                status = 500
            payload = {'result': result, 'routine': method_request.name}
            method_response = MethodResponse.create_from_method_request(
                method_request, status, payload
            )

            await device_client.send_method_response(method_response)
            await device_client.patch_twin_reported_properties({'routine': method_request.name})
    except KeyboardInterrupt:
        pass
    finally:
        if device_client is not None:
            _logger.debug('Attempting to disconnect device client')
            await device_client.disconnect()
            _logger.info('Successfully disconnected device client')
        _clear__outputs()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
