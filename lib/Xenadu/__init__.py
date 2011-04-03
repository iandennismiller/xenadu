import sys, traceback, os.path, os, inspect, re, os, tempfile, logging
from optparse import OptionParser
from string import Template

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

class Core(object):
    registry = None
    logger = None
    config = {}
    env = {}

    def __init__(self):
        self.command_line = OptionParser()
        self.command_chosen = {}
        self.init_logger()

    def init_logger(self):
        Core.logger = logging.getLogger("Xenadu")
        Core.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        Core.logger.addHandler(ch)

    def process_cmdline(self):
        #self.command_line.add_option("--config", help="config file path")
        (options, args) = self.command_line.parse_args()

        for option in Core.registry.options.keys():
            if getattr(options, option):
                self.command_chosen[option] = getattr(options, option)

        #self.load_config(options)

        for option in self.command_chosen.keys():
            Core.logger.info("calling " + option)
            function = Core.registry.tasks[option]
            function(self.command_chosen[option])

    def load_config(self, options):
        try:
            config_file = getattr(options, "config")
        except KeyError:
            print "exception: no config file"


        try:
            execfile(config_file, globals(), Core.config)
            Core.logger.info("config file: " + config_file)
            Core.config["filename"] = getattr(options, "config")
        except IOError:
            traceback.print_tb(sys.exc_info()[2])
            Core.logger.error("Xenadu cannot load or execute config file '%s'; exiting." % config_file)
            sys.exit()
        
        try:
            dom0_config_filename = Core.config["xen"]["dom0_config"]
        except KeyError:
            dom0_config_filename = 0
            Core.logger.warn("There is no dom0 config file.  Is this a Xen root domain?")

        if dom0_config_filename:
            try:
                host_hash = {}
                Core.logger.info("dom0 config file: " + dom0_config_filename)
                execfile(Core.config["xen"]["dom0_config"], globals(), host_hash)
                Core.config["dom0"] = host_hash
            except IOError:
                traceback.print_tb(sys.exc_info()[2])
                Core.logger.warn("Xenadu cannot load or execute config file '%s'; exiting" % dom0_config_filename)
                sys.exit()

    def start(self):
        Core.env = {
            'cwd': os.getcwd(),
            #'tmp_path': tempfile.mkdtemp(suffix='xenadu'),
            'tmp_path': "/tmp/xenadu",
            'guest_path': os.path.dirname(os.path.abspath(config_file))
        }

        Core.registry = Registry(self)
        Core.registry.update()
        self.process_cmdline()

class XenaduConfig(object):
    def __init__(self):
        X = Language()
        for i in file_list:
            X.add(i[0], i[1], i[2])

        c = Core()
        c.config['mapping'] = X.get_hash()
        c.start()

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

    def add(self, dest, content, perm_hash=Perm.root_644):
        caller = inspect.stack()[1][4][0]
        match = re.match(r'.+\.add\(\".*?\", (.*)\)', caller)
        if match:
            generator = match.group(1)
        else:
            generator = ""
        
        owner = perm_hash['owner']
        group = perm_hash['group']
        perm = perm_hash['perm']

        self.mapping[dest] = {
            "content": content,
            "owner": owner,
            "group": group,
            "perm": perm,
            "generator": generator,
        }

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
                mod.register()
                self.Core.logger.debug("loading: %s" % mod_name)

def f(filename):
    src_file = os.path.join(Core.env['guest_path'], 'files', filename)
    #    src_file = "%(xenadu_path)s/files/" % Core.context.config  + filename
    try:
        file = open(src_file, 'r').read()
        return file
    except:
        Core.logger.warn("problem opening file: %s" % src_file)
        return ""

def common(filename):
    return "../../_common/%s" % filename

"""
def template(template_string):
    template_hash = {}
    
    for item in Core.context.guest["config"]:
        template_hash["xenadu_%s" % item] = Core.context.guest["config"][item]
        
    template = Template(template_string)

    return template.safe_substitute(template_hash)
"""
    
def file_common(filename):
    return f(common(filename))

def template_file(filename):
    return template(f(filename))
