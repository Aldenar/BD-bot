import discord
import asyncio
import logging
import os
import json


class bd_bot(discord.Client):
    active = bool
    logger = None
    servers = dict
    config = dict
    admins = dict

    def __setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('(%(asctime)s) %(levelname)s - "%(message)s" in %(module)s/%(funcName)s')
        fh = logging.FileHandler('bot.log', 'w')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.info("Initializing!")

    @staticmethod
    def __create_conf():
        config = {
            "global_settings": {

        },
            "server_lobbies": {

            },
            "admins": {

            }
        }
        if not os.path.isdir('conf'):
            os.mkdir('conf')
        sett_json = json.dumps(config, sort_keys=True)
        f = open('conf/main.json', 'w')
        f.write(sett_json)
        f.close()
        return

    def __load_conf(self):
        repair_conf = False
        if not os.path.isfile('conf/main.json'):
            self.__create_conf()

        file = open('conf/main.json', 'r')

        if file.closed:
            self.logger.critical("Failed to open main configuration file!")
            raise RuntimeError("Failed to open main configuration file!")

        config_dict = json.load(file)

        if 'server_lobbies' not in config_dict:
            repair_conf = True
            config_dict['server_lobbies'] = {}
        self.servers = config_dict['server_lobbies']

        if 'global_settings' not in config_dict:
            repair_conf = True
            config_dict['global_settings'] = {}
        self.config = config_dict['global_settings']

        if 'admins' not in config_dict:
            repair_conf = True
            config_dict['admins'] = {}
        self.admins = config_dict['admins']

        if repair_conf:
            settings = {'server_lobbies': self.servers, 'global_settings': self.config, 'admins': self.admins}
            file = open('conf/main.json', 'w')
            json.dump(settings, file, sort_keys=True)

    def __load_modules(self):
        path=""
        if "module_dir" in self.config:
            path=self.config["module_dir"]
        else:
            path="modules/"

        if (not os.path.isdir(path)):
            self.logger.error("No modules directory found!")
            self.active = False
            return

        

    def debug(self):
        self.__load_conf()

    def __init__(self):
        self.__setup_logger()
        self.__load_conf()
        super(bd_bot, self).__init__(cache_auth=True)

    @asyncio.coroutine
    async def on_ready(self):
        self.logger.info("Client is ready!")
        self.active = True

    @asyncio.coroutine
    async def on_message(self, message):
            return None

    @asyncio.coroutine
    async def on_member_join(self, member):
        return None

    @asyncio.coroutine
    async def on_error(self, event, *args, **kwargs):
        self.logger.error("An error has occurred in the event {}[args={}, kwargs={}]".format(event, args, kwargs))
        super(bd_bot, self).on_error(event, args, kwargs)
