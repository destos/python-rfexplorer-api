# -*- coding: utf-8 -*-
import logging
import logging.config

import click
import yaml

from rfexplorer import RFExplorer

# TODO: look up implementing a repl that can perform lots of functions without
# having to run the cli multiple times
# would be usful for quickly searching channels to see if they're in use.


with open('logging.yaml') as f:
    config = yaml.load(f)
    config.setdefault('version', 1)
    logging.config.dictConfig(config)


logger = logging.getLogger(__name__)


@click.command()
@click.option('-p', '--port', prompt='port of the RFExplorer',
              help='full path for unix, com# for windows')
@click.option('-fpv', '--fpv-scan', is_flag=True)
def main(port, fpv_scan):
    """Console script for rfexplorer_api"""

    try:
        logger.info('wat')
        rfe = RFExplorer(port)
        rfe.connect()
        print(rfe.get_config())

        # Testing
        rfe.send_sweep_params(514700, 523200, -60, -100)
        print(rfe.get_config())

        if fpv_scan:
            import fpv_bands
            channels = fpv_bands.all_channels
            first_channel = channels[0]
            last_channel = channels[-1]

            # Scan the range of FPV frequencies and see what's being used
            result = rfe.scan_spectrum(
                first_channel.frequency,
                last_channel.frequency,
                section_scan_delay=2)

            # Use result and then see where the spikes corelate with channels
            # then map those channels and see if there is a better setup
            # If channels are too close let us know

    except Exception as e:
        logger.error(e)
    finally:
        rfe.disconnect()


if __name__ == "__main__":
    main()
