import argparse

from lib.helpers import read_json_file
from lib.watchdog import WatchDog
from lib.configuration import Configuration

class App():
    def __init__(self, config_filename):
        config = read_json_file(config_filename)

        config = Configuration(config)

        self.watchdog = WatchDog(config)
    
    def run(self):
        self.watchdog.monitor()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LB2120 modem celltower watchdog')
    parser.add_argument('-c','--config', help='Configuration_file', required=True)
    args = vars(parser.parse_args())

    APP = App(args['config'])
    APP.run()
