from Xenadu.Core import Core
import os, shutil, subprocess, string, re

def clean(dummy):
    errors = []
    try:
        shutil.rmtree(os.path.join(Core.env["tmp_path"], "build"))
    except OSError, why:
        print why

def do_build(file_mapping):
    for dest_filename in file_mapping:
        dst_file = "%s/build/.%s" % (Core.env["tmp_path"], dest_filename)
        
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

    do_build(Core.config["mapping"])
    
def simulate(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-crnv",
        "%s/build/" % Core.env["tmp_path"], 
        "%(user)s@%(address)s:/" % Core.config["ssh"]],
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

def register():
    Core.registry.register_task(name="clean", args=0, help="remove build path", function=clean)
    Core.registry.register_task(name="build", args=0, help="build files for host", function=build)
    Core.registry.register_task(name="simulate", args=0, help="simulate deploy config to remote host", function=simulate)
    Core.registry.register_task(name="deploy", args=0, help="deploy config to remote host", function=deploy)
