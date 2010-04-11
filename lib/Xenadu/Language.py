from Xenadu.Core import Core
from string import Template
import inspect, re, os

def file(filename):
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
    return file(common(filename))

def template_file(filename):
    return template(file(filename))

class Language(object):

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

    def __init__(self):
        self.mapping = {}

    def add(self, dest, content, perm_hash=root_644):
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
    
