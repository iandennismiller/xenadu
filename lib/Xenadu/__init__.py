from __future__ import with_statement
import sys, traceback, os.path, os, inspect, re, os, tempfile, logging
from optparse import OptionParser
from string import Template

Env = {}

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class Core(object):
    def __init__(self):
        self.init_logger()
        self.command_line = OptionParser()
        self.command_chosen = {}
        Env['Core'] = self
        Env['Config'] = {
            'cwd': os.getcwd(),
            'tmp_path': "/tmp/xenadu"
        }
        Env['Registry'] = Registry(self)
        Env['Registry'].update()

    def init_logger(self):
        logger = logging.getLogger("Xenadu")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    def start(self):
        for option in self.command_chosen.keys():
            logging.getLogger("Xenadu").debug("calling " + option)
            function = Env['Registry'].tasks[option]
            function(self.command_chosen[option])

class XenaduConfig(object):
    def __init__(self, env, mapping):
        self.c = Core()
        self.mapping = mapping
        Env['Config'].update(env)
        if 'guest_path' not in Env["Config"]:
            Env["Config"]['guest_path'] = os.path.dirname(os.path.abspath(sys.argv[0]))
        logging.getLogger("Xenadu").info("path is: %s " % Env["Config"]['guest_path'])

        # process command line
        Env['Core'].command_line.add_option("-p", help="profile to use")
        (options, args) = Env['Core'].command_line.parse_args()
        for option in Env["Registry"].options.keys():
            if getattr(options, option):
                Env['Core'].command_chosen[option] = getattr(options, option)
        
        profile = getattr(options, "p")
        if profile:
            Env['Profile'] = profile
            logging.getLogger("Xenadu").info("profile is: %s " % Env['Profile'])
        else:
            Env['Profile'] = None

        X = Language()
        for i in self.mapping:
            X.add(i[0], i[1], i[2])
        Env['Config']['mapping'] = X.get_hash()
        #print Env['Config']
        self.c.start()

class Perm(object):
    root_644 = {
        "perm": "0644", 
        "owner": "root", 
        "group": "root" 
    }

    root_755 = {
        "perm": "0755", 
        "owner": "root", 
        "group": "root" 
    }

    root_600 = {
        "perm": "0600", 
        "owner": "root", 
        "group": "root" 
    }

    root_440 = {
        "perm": "0440", 
        "owner": "root", 
        "group": "root" 
    }

class Language(object):
    def __init__(self):
        self.mapping = {}

    def add(self, dest, src, perm_hash=Perm.root_644):        
        #try:
        #with open(src) as f:
        #    content = f.read()

        self.mapping[dest] = {
            #"content": content,
            "local_file": src,
            "remote_file": dest,
            #"generator": generator,
        }

        self.mapping[dest].update(perm_hash)

    def get_hash(self):
        return self.mapping

class Registry(object):
    def __init__(self, Core):
        self.Core = Core
        self.tasks = {}
        self.options = {}

    def register_function(self, option, function):
        self.tasks[option] = function

    def register_option(self, option, help):
        self.Core.command_line.add_option("--" + option, action="store_true", help=help)
        self.options[option] = 1

    def register_argument(self, option, help):
        self.Core.command_line.add_option("--" + option, help=help)
        self.options[option] = 1

    def register_task(self, name, args, help, function):
        if args > 0:
            self.register_argument(name, help)
        else:
            self.register_option(name, help)
        self.register_function(name, function)

    def update(self):
        m = __import__("Xenadu.Task")
        for task in dir(m.Task):
            if not re.search(r'^__', task):
                mod_name = "Xenadu.Task.%s" % task
                mod = sys.modules[mod_name]
                logging.getLogger("Xenadu").debug("loading: %s" % mod_name)
                mod.register()
