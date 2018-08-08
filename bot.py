import discord
import asyncio
import logging
import os
import json
import importlib.util


class bd_bot(discord.Client):
    active = bool
    logger = None
    server_lobbies = dict
    config = dict
    admins = dict
    module_dir = ""
    modules = []
    hooks = {}

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
                "module_dir": "modules/"
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
#        if 'server_lobbies' not in config_dict:
#            repair_conf = True
#            config_dict['server_lobbies'] = {}
#        self.server_lobbies = config_dict['server_lobbies']

        if 'global_settings' not in config_dict:
            repair_conf = True
            config_dict['global_settings'] = {"module_dir": "modules/"}
        self.config = config_dict['global_settings']

#        if 'admins' not in config_dict:
#            repair_conf = True
#            config_dict['admins'] = {}
#        self.admins = config_dict['admins']

        if repair_conf:
            settings = {'server_lobbies': self.server_lobbies, 'global_settings': self.config, 'admins': self.admins}
            file = open('conf/main.json', 'w')
            json.dump(settings, file, sort_keys=True)

    def __check_set_hooks(self, module):
        for hook in module.hooks:
            if (getattr(module, hook) is None):
                self.logger.warn("No corresponding event hook function found for {}!".format(hook))
                module.hooks.remove(hook)
                continue
            if (getattr(super(bd_bot, self), hook) is None):
                self.logger.warn("No such event hook available {}!".format(hook))
                module.hooks.remove(hook)
                continue
            if (getattr(self,hook) is None):
                self.logger.warn("Unknown / unsupported event hook {}!".format(hook))
                module.hooks.remove(hook)
                continue


    def __check_modules(self):
        for module in self.modules:
            hooks = getattr(module, "hooks")
            init = getattr(module, "init")
            if (hooks is None) or (init is None):
                self.modules.remove(module)
                self.logger.warning("Invalid module {}, no hooks table or init method found!".format(module))

    def __import_modules(self, module_array):
        self.logger.info("Importing modules!")
        for module in module_array:
            if not os.path.isfile(module):
                self.logger.warning("Module file {} not found!".format(module))
                continue

            #Dynamic module loading from file
            spec = importlib.util.spec_from_file_location(module, self.module_dir+"/"+module)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            #And we store it in a global modules array
            self.modules.append(module)
        self.__check_modules()



    def __get_modules(self):

        if "module_dir" in self.config:
            self.module_dir  = self.config["module_dir"]
            self.logger.info("Module dir set by config")
        else:
            self.module_dir = "modules/"
            self.logger.info("Module dir set statically")

        if not os.path.isdir(path):
            self.logger.error("No modules directory found!")
            self.active = False
            return

        for (dirpath, dirname, filenames) in os.walk(self.module_dir):
            for file in filenames:
                if os.path.splitext(file)[1].lower() != '.py':
                    filenames.remove(file)
        self.__import_modules(filenames)


        self.logger.info("Finished loading modules!")

        return



    def debug(self):
        self.__load_conf()

    def __init__(self):
        self.__setup_logger()
        self.__load_conf()
        self.__get_modules()
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
