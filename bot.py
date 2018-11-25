import discord
import asyncio
import logging
import os
import json
import sys
import importlib.util


class bd_bot(discord.Client):
    active = bool
    logger = None
    config = dict
    module_dir = ""
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

        if 'global_settings' not in config_dict:
            repair_conf = True
            config_dict['global_settings'] = {"module_dir": "modules/"}
        self.config = config_dict['global_settings']

        if repair_conf:
            settings = {'global_settings': self.config, 'admins': self.admins}
            file = open('conf/main.json', 'w')
            json.dump(settings, file, sort_keys=True)

    def __check_set_hooks(self, module):
        for hook in module.hooks:
            #If the module doesn't contain appropriate handler function
            if getattr(module, hook, None) is None:
                self.logger.warning("No corresponding event hook \"{}\" function found (module \"{}\")".format(hook, module.name))
                return
            #If we did not yet implement the event handler
            if getattr(discord, hook, None) is None:
                self.logger.warning("No such event hook \"{}\" available (module \"{}\")!".format(hook, module.name))
                return
            #If the event handler doesn't exist at all
            if getattr(self, hook, None) is None:
                self.logger.warning("Unknown / unsupported event hook \"{}\" (module \"{}\")!".format(hook, module.name))
                return
            self.hooks[hook] += module

    def __check_module(self, module):
        hooks = getattr(module, "hooks", None)
        name = getattr(module, "name", None)
        init = getattr(module, "init", None)
        if (hooks is None) or (name is None) or (init is None):
            self.logger.warning("Invalid module {}, no hooks table, name or init method found!".format(module))
            return
        self.__check_set_hooks(module)

    def __import_modules(self, module_array):
        self.logger.info("Importing modules!")
        for module in module_array:
            if not os.path.isfile(self.module_dir+module):
                self.logger.warning("Module file {} not found!".format(module))
                continue

            #Dynamic python source code loadup from file
            spec = importlib.util.spec_from_file_location(module, self.module_dir+module)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            #And we store it in a global modules array
            self.__check_module(module)

    def __get_modules(self):

        if "module_dir" in self.config:
            self.module_dir = self.config["module_dir"]
            if self.module_dir[len(self.module_dir)-1] != '/':
                self.module_dir += "/"
            self.logger.info("Module dir set by config")
        else:
            self.module_dir = "modules/"
            self.logger.info("Module dir set statically")

        if not os.path.isdir(self.module_dir):
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
        self.logger.info("Init phase done!")

    @asyncio.coroutine
    async def on_ready(self):
        self.logger.info("Client is ready!")
        for module in self.hooks["on_ready"]:
            module.on_ready(self)
        self.active = True

    @asyncio.coroutine
    async def on_message(self, message):
        self.logger.info("Received a message!")
        self.hooks = self.hooks
        try:
            for module in self.hooks["on_message"]:
                module.on_message(self, message)
        except:
            self.logger.exception("Got an exception: "+sys.exc_info()[0])

    @asyncio.coroutine
    async def on_member_join(self, member):
        self.logger.info("A new member joined!!")
        self.hooks = self.hooks
        try:
            for module in self.hooks["on_message"]:
                module.on_member_join(self, member)
        except:
            self.logger.exception("Got an exception: " + sys.exc_info()[0])

    @asyncio.coroutine
    async def on_error(self, event, *args, **kwargs):
        self.logger.error("An error has occurred in the event {}[args={}, kwargs={}]".format(event, args, kwargs))
        super(bd_bot, self).on_error(event, args, kwargs)
