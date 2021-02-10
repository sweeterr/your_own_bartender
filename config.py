import yaml


CONFIG_FILE = "config.yml"


class Config:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.bot = {}
        self.server = {}
        self.data = {}
        self.emoji = {}
        self.get_config()

    def get_config(self):
        with open(self.config_file, "r", encoding="utf-8") as file:
            config = yaml.load(file, Loader=yaml.Loader)
        self.bot['token'] = config["bot"]["token"]
        self.bot['allowed'] = config['bot']['allowed']
        self.server['address'] = config['server']['address']
        self.data["tree"] = config["data"]["tree"]
        self.data["recipes"] = config["data"]["recipes"]
        self.emoji["cocktail"] = config["emojis"]["tropical"]["emoji"]
        self.emoji["notes"] = config["emojis"]["woman_dancing"]["emoji"]
        self.emoji["instructions"] = config["emojis"]["hammer_wrench"]["emoji"]
        self.emoji["ingredients"] = config["emojis"]["list"]["emoji"]
        print(self.emoji)


def main():
    Config()


if __name__ == '__main__':
    main()
