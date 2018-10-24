import json
import datetime
import time
import requests
import argparse
import re

from bs4 import BeautifulSoup

CONFIGURATION = None
SESSION = None
TOKEN = None

class Configuration():
    def __init__(self, config_dict):
        valid = True

        self.permission_levels = {
            'Admin': 1,
            'Guest': 0
        }

        self.modem_ip = config_dict.get('modem_ip')

        if not self.modem_ip:
            print(f'Add modem ip to config file: "modem_ip": "[MODEM_IP]"')
            valid = False
        
        self.password_hash = config_dict.get('password_hash')

        if not self.password_hash:
            print(f'Add password hash to config file: "password_hash": "[PASSWORD_HASH]"')
            valid = False
        
        self.preferred_celltower = config_dict.get('preferred_celltower')

        if not self.preferred_celltower:
            print(f'Add prefered celltower ID to config file: "preferred_celltower": "[PREFERRED_CELLTOWER_ID]"')
            valid = False
        else:
            self.preferred_celltower = int(self.preferred_celltower)
        
        self.reboot_window = config_dict.get('reboot_window')

        if self.reboot_window and re.match(r'^\d{1,2}\:\d{1,2}$', self.reboot_window):
            window = self.reboot_window.split(':')

            if window[0] <= window[1]:
                self.reboot_window = window
        
        self.debug = config_dict.get('debug') or False

        self.auto_reboot = config_dict.get('auto_reboot') or False

        self.check_interval = config_dict.get('check_interval') or 300

        self.max_retries = config_dict.get('max_retries') or 3
        
        self.valid = valid

def print_current_config():
    global CONFIGURATION

    debug_print('Current configuration:')

    v = vars(CONFIGURATION)

    for key, val in v.items():
        debug_print(f'\t{key} ({type(val)}): {val}')


def get_current_permissions():
    global CONFIGURATION

    url = f'http://{CONFIGURATION.modem_ip}/api/session.json'

    request = SESSION.get(url)

    data = load_json_string(request.text)

    permission = data['session']['userRole']

    return permission

def login():
    global CONFIGURATION
    global TOKEN
    global SESSION

    TOKEN = get_token()

    url = f'http://{CONFIGURATION.modem_ip}/Forms/config?token={TOKEN}&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password={CONFIGURATION.password_hash}'

    _ = SESSION.get(url)

def requires_permission(permission):
    def decorator(func):
        def decorated(*args, **kwargs):
            global CONFIGURATION

            current_permission = get_current_permissions()

            if CONFIGURATION.permission_levels[current_permission] < CONFIGURATION.permission_levels[permission]:
                debug_print('Elevating permissions')
                
                login()

            return func(*args, **kwargs)
        
        return decorated
    
    return decorator

@requires_permission('Admin')
def get_model():
    global CONFIGURATION
    global SESSION

    url = f'http://{CONFIGURATION.modem_ip}/api/model.json'

    request = SESSION.get(url)

    data = load_json_string(request.text)

    return data

@requires_permission('Admin')
def reboot():
    global SESSION
    global CONFIGURATION
    global TOKEN

    url = f'http://{CONFIGURATION.modem_ip}/Forms/config?general.routerReset=1&err_redirect=/error.json&ok_redirect=/success.json&token={TOKEN}&general.shutdown=Restart'

    _ = SESSION.get(url)

def get_celltower_id():
    data = get_model()

    celltower_id = int(data['wwanadv']['cellId'])

    return celltower_id

def is_up():
    global CONFIGURATION
    global SESSION

    url = f'http://{CONFIGURATION.modem_ip}/index.html'

    try:
        _ = SESSION.get(url)
    except requests.exceptions.ConnectionError:
        return False
    except Exception as err:
        c = type(err).__name__
        m = str(err)
        debug_print(f'({c}) {m}')

        return False
    
    return True

def get_token():
    global CONFIGURATION
    global SESSION

    url = f'http://{CONFIGURATION.modem_ip}/index.html'

    request = SESSION.get(url)

    soup = BeautifulSoup(request.text, features="html.parser")

    token = soup.find_all('input', {'name': 'token'})[0].get('value')

    return token

def load_json_file(filename):
    with open(filename, 'r') as input_file:
        data = json.load(input_file)

        return data

def load_json_string(data):
    data = data.replace('\t', '')
    data = data.replace('\n', '')
    data = data.replace(' ', '')
    if data[0] != '{':
        return json.loads(''.join(['{', data, '}']))
    return json.loads(data)

def create_session():
    session = requests.Session()

    return session

def debug_print(message):
    global CONFIGURATION

    if CONFIGURATION.debug:
        timestamp_print(f'[DEBUG] {message}')

def get_current_hour():
    return datetime.datetime.now().hour

def timestamp_print(message):
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%H:%M:%S.%f')
    print(f'{timestamp} - {message}')

def is_in_range(val, rn):
    return rn[0] <= val <= rn[1]

def has_rebooted():
    debug_print('Checking if modem has rebooted')

    if is_up():
        debug_print('Modem has rebooted')
        return True
    
    return False

def handle_reboot():
    global CONFIGURATION

    max_retries = CONFIGURATION.max_retries
    current_retries = 1

    # Reboot loop
    while True:
        do_reboot = False
        auto = CONFIGURATION.auto_reboot

        if auto:
            debug_print('Auto reboot is enabled.')
            do_reboot = True
        else:
            debug_print('User chose to reboot.')
            valid = ['y', 'yes']
            answer = input('Do you want to reboot?').strip().lower()

            if answer in valid:
                do_reboot = True
            else:
                debug_print('User chose to not reboot.')
                break
        
        if do_reboot:
            if auto and CONFIGURATION.reboot_window:
                current_hour = get_current_hour()
                window = CONFIGURATION.reboot_window
                if not is_in_range(current_hour, window):
                    debug_print(f'Outside of auto reboot time window {current_hour} ({window[0]}:{window[1]})')
                    break

                debug_print(f'Rebooting. {current_retries} / {max_retries} attempts.')
                reboot()
            else:
                debug_print('Rebooting.')
                reboot()

            # Wakeup loop
            while not has_rebooted():
                time.sleep(5)
        
        celltower_id = get_celltower_id()

        if celltower_id == CONFIGURATION.preferred_celltower:
            debug_print('Celltower changed successfully.')
            break
        else:
            current_retries += 1
        
        if auto and current_retries >= max_retries:
            debug_print('Max retries exceeded')
            break

def run(config_filename):
    global CONFIGURATION
    global SESSION
    global TOKEN

    data = load_json_file(config_filename)

    CONFIGURATION = Configuration(data)

    if not CONFIGURATION.valid:
        return
    
    if CONFIGURATION.debug:
        print_current_config()
    
    SESSION = create_session()

    try:
        # Main loop
        while True:
            debug_print('Checking celltower')
            celltower_id = get_celltower_id()

            if celltower_id != CONFIGURATION.preferred_celltower:
                debug_print(f'Celltower has changed to {celltower_id}')

                handle_reboot()
            
            interval = CONFIGURATION.check_interval

            debug_print(f'Checking again in {interval} seconds')

            time.sleep(interval)
    
    except KeyboardInterrupt:
        debug_print('User stopped the monitor')
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LB2120 modem celltower watchdog')
    parser.add_argument('-c','--config', help='Configuration_file', required=True)
    args = vars(parser.parse_args())

    run(args['config'])
