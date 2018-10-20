import requests
import time

from bs4 import BeautifulSoup

from lib.helpers import read_json_string

class WatchDog():
    def __init__(self, config):
        if not config.valid:
            return

        self.config = config

        self.session = None
    
    def monitor(self):
        try:
            while True:
                self.session = self._create_session()

                token = self._get_security_token()

                celltower_id = self._get_celltower_id(token)

                if celltower_id != self.config.preferred_celltower_id:
                    print(f'Celltower has changed to {celltower_id}.')

                    valid = ['y', 'yes']

                    reboot = input('Do you want to reboot the modem?').lower()

                    if reboot in valid:
                        print('Attempting to reboot the modem.')

                        rebooted = self._reboot(token)

                        if rebooted:
                            print('Reboot success')
                        else:
                            print('Reboot failed')
                interval = self.config.check_interval

                print(f'Checking again in {interval} seconds')
                time.sleep(interval)
        except KeyboardInterrupt:
            print('Stopping the monitor.')

            return

    def _get_celltower_id(self, token):
        login_url = f'http://{self.config.modem_ip}/Forms/config?token={token}&ok_redirect=%2Findex.html&err_redirect=%2Findex.html&session.password={self.config.password_hash}'

        request = self.session.get(login_url)

        config_url = f'http://{self.config.modem_ip}/api/model.json'

        request = self.session.get(config_url)

        data = read_json_string(request.text)

        celltower_id = str(data['wwanadv']['cellId'])

        return celltower_id
    
    def _get_security_token(self):
        request = self.session.get(f'http://{self.config.modem_ip}/index.html')

        soup = BeautifulSoup(request.text, features="html.parser")

        token = soup.find_all('input', {'name': 'token'})[0].get('value')

        return token

    def _create_session(self):
        session = requests.Session()

        return session
    
    def _reboot(self, token):
        url = f'http://{self.config.modem_ip}/Forms/config?general.routerReset=1&err_redirect=/error.json&ok_redirect=/success.json&token={token}&general.shutdown=Restart'
        
        request = self.session.get(url)

        status_code = request.status_code

        if status_code == 200:
            return True
        
        return False
