from Xenadu.Core import Core
import os, shutil, subprocess, string, re, sys

def lookup_file(filename, file_mapping=None):
    if file_mapping == None:
        file_mapping = Core.config["mapping"]
    try:
        generator = file_mapping[filename]["generator"]
    except KeyError:
        Core.logger.error("cannot find file %s" % filename)
        sys.exit()
    
    m = re.search(r"[file|file_common]\(\"(.*)\"\)", generator)
    return m

def slurp_remote(filename, file_mapping=None):
    m = lookup_file(filename, file_mapping)
    
    dst_file = os.path.join(Core.env["guest_path"], "files", m.group(1))
    Core.logger.info("remote file: %s, local file: %s" % (filename, dst_file))
    subprocess.Popen(["/usr/bin/scp", 
        "%s@%s:%s" % (Core.config["ssh"]["user"], Core.config["ssh"]["address"], filename), 
        dst_file])

def diff(filename, file_mapping=None):
    m = lookup_file(filename, file_mapping)
    
    dst_file = os.path.join(Core.env["tmp_path"], "diff")
    diff_file = os.path.join(Core.env["tmp_path"], "diff.orig")
    local_file = os.path.join(Core.env["tmp_path"], "build", ".%s" % filename)
    Core.logger.info("diff remote file: %s, local file: %s" % (filename, local_file))

    file = open(diff_file, "w")
    file.write(Core.config["mapping"][filename]["content"])
    file.close()

    output = subprocess.Popen(["/usr/bin/scp", 
        "%s@%s:%s" % (Core.config["ssh"]["user"], Core.config["ssh"]["address"], filename), 
        dst_file]).communicate()[0]

    output = subprocess.Popen(["/usr/bin/diff", dst_file, diff_file],
        stdout=subprocess.PIPE).communicate()[0]

    print output

def slurp_local(dest_filename, file_mapping = None):
    if file_mapping == None:
        file_mapping = Core.context.config["mapping"]    
    
    for filename in file_mapping:
        m = re.search(r'file\(\"(.*)\"\)', file_mapping[filename]["generator"])
        if m and m.group(1) == dest_filename:
            slurp_remote(filename)
            return
    
    Core.logger.error("couldn't find a match for: %s" % dest_filename)

def slurp_all(dummy, file_mapping = None):
    if file_mapping == None:
        file_mapping = Core.context.guest["mapping"]

    for filename in file_mapping:
        slurp(filename)

def register():
	Core.registry.register_task(name="slurp.local", args=1, help="copy file from remote host based on local filename", function=slurp_local)
	Core.registry.register_task(name="slurp.remote", args=1, help="copy file based on remote filename", function=slurp_remote)
	Core.registry.register_task(name="slurp.all", args=0, help="copy all files from remote host", function=slurp_all)
	Core.registry.register_task(name="diff.remote", args=1, help="diff remote file with local version", function=diff)
