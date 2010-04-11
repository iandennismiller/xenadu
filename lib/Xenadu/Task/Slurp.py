from Xenadu.Core import Core
import os, shutil, subprocess, string, re

def slurp_remote(filename, file_mapping=None):
    if file_mapping == None:
        file_mapping = Core.context.config["mapping"]
        
    generator = file_mapping[filename]["generator"]
    m = re.search(r"file\(\"(.*)\"\)", generator)
    
    if m:
        dst_file = "%(xenadu_path)s/files/" % Core.context.config + m.group(1)
        
        Core.context.logger.info("remote file: %s, local file: %s" % (filename, dst_file))

        subprocess.Popen(["/usr/bin/scp", 
            "%s:%s" % (Core.context.config["ssh_user"], filename), 
            dst_file])
    else:
        Core.context.logger.error("couldn't find a match for: %s" % filename)

def slurp_local(dest_filename, file_mapping = None):
    if file_mapping == None:
        file_mapping = Core.context.config["mapping"]    
    
    for filename in file_mapping:
        m = re.search(r'file\(\"(.*)\"\)', file_mapping[filename]["generator"])
        if m and m.group(1) == dest_filename:
            slurp_remote(filename)
            return
    
    Core.context.logger.error("couldn't find a match for: %s" % dest_filename)

def slurp_all(dummy, file_mapping = None):
    if file_mapping == None:
        file_mapping = Core.context.guest["mapping"]

    for filename in file_mapping:
        slurp(filename)

def register():
	Core.registry.register_task(name="slurp.local", args=1, help="copy file from remote host based on local filename", function=slurp_local)
	Core.registry.register_task(name="slurp.remote", args=1, help="copy file based on remote filename", function=slurp_remote)
	Core.registry.register_task(name="slurp.all", args=0, help="copy all files from remote host", function=slurp_all)
