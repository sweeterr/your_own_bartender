import yaml


CONFIG_FILE = "config.yml"


class Config:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.bot = {}
        self.server = {}
        self.get_config()

    def get_config(self):
        with open(self.config_file, "r") as file:
            config = yaml.load(file, Loader=yaml.Loader)
        self.bot['token'] = config["bot"]["token"]
        self.bot['allowed'] = config['bot']['allowed']
        self.server['address'] = config['server']['address']
        # print(self.server)


def main():
    Config()


if __name__ == '__main__':
    main()
