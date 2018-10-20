class Configuration():
    def __init__(self, config):
        valid = True

        self.modem_ip = config.get('modem_ip')

        if not self.modem_ip:
            print('Please add line "modem_ip": "[YOUR MODEM IP HERE]" to the configuration file.')
            valid = False
        
        preferred_celltower_id = config.get('celltower_id')

        if not preferred_celltower_id:
            print('Please add line "celltower_id": "[YOUR PREFERRED CELLTOWER ID HERE]" to the configuration file.')
            valid = False
        else:
            self.preferred_celltower_id = str(preferred_celltower_id)

        self.password_hash = config.get('password_hash')

        if not self.password_hash:
            print('Please add line "password_hash": "[YOUR PASSWORD HASH HERE]" to the configuration file.')
            valid = False

        self.check_interval = config.get('check_interval') or 300

        self.valid = valid