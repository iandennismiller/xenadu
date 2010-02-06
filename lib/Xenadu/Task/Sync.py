from Xenadu.Core import Core
import os, shutil, subprocess, string, re

def clean(dummy):
    errors = []
    try:
        shutil.rmtree(Core.context.globals["tmp_path"]+"/build")
    except OSError, why:
        print why

def do_build(file_mapping):
    for dest_filename in file_mapping:
        dst_file = "%s/build/.%s" % (Core.context.globals["tmp_path"], dest_filename)
        
        try:
            os.makedirs(os.path.dirname(dst_file))
        except:
            pass
        
        out_filehandle = open(dst_file, "w")
        out_filehandle.write(file_mapping[dest_filename]["content"])
        out_filehandle.close()
        
        os.chmod(dst_file, string.atoi(file_mapping[dest_filename]["perm"], 8))

def build(dummy):
    clean(0)

    do_build(Core.context.config["mapping"])
    
def simulate(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-crnv",
        "%s/build/" % Core.context.globals["tmp_path"], 
        "%s:/" % Core.context.config["ssh_user"]], 
        stdout=subprocess.PIPE).communicate()[0]
    print output

def deploy(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-rpv",
        "%s/build/" % Core.context.globals["tmp_path"], 
        "%s:/" % Core.context.config["ssh_user"]], 
        stdout=subprocess.PIPE).communicate()[0]
    print output
    
    chown_cmd = ""
        
    for dst_file in Core.context.config["mapping"]:
        chown_cmd = chown_cmd + "chown %s:%s %s;" % (
            Core.context.config["mapping"][dst_file]["owner"], 
            Core.context.config["mapping"][dst_file]["group"], dst_file)

    subprocess.Popen(["/usr/bin/ssh",
        "root@%s" % Core.context.config["hostname"],
        chown_cmd])

    output = subprocess.Popen(["/usr/bin/ssh",
        "root@%s" % Core.context.config["hostname"],
        Core.context.config["spinup"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output

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
	Core().registry.register_task(name="deploy", args=0, help="deploy config to remote host", function=deploy)
	Core().registry.register_task(name="simulate", args=0, help="simulate deploy config to remote host", function=simulate)
	Core().registry.register_task(name="build", args=0, help="build files for host", function=build)
	Core().registry.register_task(name="clean", args=0, help="remove build path", function=clean)
	Core().registry.register_task(name="slurp.local", args=1, help="copy file from remote host based on local filename", function=slurp_local)
	Core().registry.register_task(name="slurp.remote", args=1, help="copy file based on remote filename", function=slurp_remote)
	Core().registry.register_task(name="slurp.all", args=0, help="copy all files from remote host", function=slurp_all)
