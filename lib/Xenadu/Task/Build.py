import Xenadu
import os, shutil, subprocess, string, re

def clean(dummy):
    errors = []
    try:
        shutil.rmtree(os.path.join(Xenadu.Env["Core"].config["tmp_path"], "build"))
    except OSError, why:
        print why

def do_build(file_mapping):
    for dest_filename in file_mapping:
        dst_file = "%s/build/.%s" % (Xenadu.Env["Core"].config["tmp_path"], dest_filename)
        
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
    do_build(Xenadu.Env["Core"].config["mapping"])
    
def simulate(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-crnv",
        "%s/build/" % Xenadu.Env["Core"].config["tmp_path"], 
        "%(user)s@%(address)s:/" % Xenadu.Env["Core"].config["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output

def deploy(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-crpv",
        "%s/build/" % Xenadu.Env["Core"].config["tmp_path"], 
        "%(user)s@%(address)s:/" % Xenadu.Env["Core"].config["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output
    
    chown_cmd = ""
        
    for dst_file in Xenadu.Env["Core"].config["mapping"]:
        chown_cmd = chown_cmd + "chown %s:%s %s;" % (
            Xenadu.Env["Core"].config["mapping"][dst_file]["owner"], 
            Xenadu.Env["Core"].config["mapping"][dst_file]["group"], dst_file)

    subprocess.Popen(["/usr/bin/ssh",
        "%(user)s@%(address)s" % Xenadu.Env["Core"].config["ssh"],
        chown_cmd])
    
def register():
    Xenadu.Env["Core"].registry.register_task(name="clean", args=0, help="remove build path", function=clean)
    Xenadu.Env["Core"].registry.register_task(name="build", args=0, help="build files for host", function=build)
    Xenadu.Env["Core"].registry.register_task(name="simulate", args=0, help="simulate deploy config to remote host", function=simulate)
    Xenadu.Env["Core"].registry.register_task(name="deploy", args=0, help="deploy config to remote host", function=deploy)
