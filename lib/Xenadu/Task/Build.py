import Xenadu
import os, shutil, subprocess, string, re, logging

def clean(dummy):
    errors = []
    try:
        shutil.rmtree(os.path.join(Xenadu.Env["Config"]["tmp_path"], "build"))
    except OSError, why:
        print why

def do_build(file_mapping):
    for dest_filename in file_mapping:
        try:
            entry = Xenadu.Env["Config"]["mapping"][dest_filename]
        except:
            logging.getLogger("Xenadu").error("can't find: %s" % dest_filename)
            return

        dst_file = "%s/build/.%s" % (Xenadu.Env["Config"]["tmp_path"], dest_filename)
        
        try:
            os.makedirs(os.path.dirname(dst_file))
        except:
            pass
        
        local_file = os.path.join(Xenadu.Env["Config"]["guest_path"], "files", entry['local_file'])
        shutil.copyfile(local_file, dst_file)

        os.chmod(dst_file, string.atoi(file_mapping[dest_filename]["perm"], 8))

def build(dummy):
    clean(0)
    do_build(Xenadu.Env["Config"]["mapping"])
    
def simulate(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-crnv",
        "%s/build/" % Xenadu.Env["Config"]["tmp_path"], 
        "%(user)s@%(address)s:/" % Xenadu.Env["Config"]["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output

def deploy(dummy):
    build(0)

    output = subprocess.Popen([
        "/usr/bin/rsync", "-crpv",
        "%s/build/" % Xenadu.Env["Config"]["tmp_path"], 
        "%(user)s@%(address)s:/" % Xenadu.Env["Config"]["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output
    
    chown_cmd = ""
        
    for dst_file in Xenadu.Env["Config"]["mapping"]:
        # this won't work for files with ' or escape chars
        chown_cmd = chown_cmd + "chown %s:%s %s;" % (
            Xenadu.Env["Config"]["mapping"][dst_file]["owner"], 
            Xenadu.Env["Config"]["mapping"][dst_file]["group"], dst_file)

    cmd = "/usr/bin/ssh %(user)s@%(address)s " % Xenadu.Env["Config"]["ssh"] + " '%s'" % chown_cmd
    os.system(cmd)
    
    #subprocess.Popen(["/usr/bin/ssh",
    #    "%(user)s@%(address)s" % Xenadu.Env["Config"]["ssh"],
    #    chown_cmd])
    
def register():
    Xenadu.Env["Registry"].register_task(name="clean", args=0, help="remove build path", function=clean)
    Xenadu.Env["Registry"].register_task(name="build", args=0, help="build files for host", function=build)
    Xenadu.Env["Registry"].register_task(name="simulate", args=0, help="simulate deploy config to remote host", function=simulate)
    Xenadu.Env["Registry"].register_task(name="deploy", args=0, help="deploy config to remote host", function=deploy)
