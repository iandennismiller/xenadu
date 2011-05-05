import os, shutil, subprocess, string, logging
from Xenadu import Language
import Xenadu

def ssh_bootstrap(dummy):
    Xenadu.Task.Build.clean(0)

    X = Language()
    X.add("/root/.ssh/authorized_keys2", "_ssh/authorized_keys2-root")
    X.add("/etc/ssh/sshd_config", "_ssh/sshd_config")
    mapping = X.get_hash()

    Xenadu.Task.Sync.do_build(mapping)

    output = subprocess.Popen(["/usr/bin/rsync", "-rpv", 
        "%s/build/" % Xenadu.Env["Core"].context.globals["tmp_path"], 
        "%(user)s@%(address)s:/" % Xenadu.Env["Config"]["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output

def ssh(command):
    logging.getLogger("Xenadu").debug("ssh: " + command)

    output = subprocess.Popen(["/usr/bin/ssh",
        "-tt",
        "%(user)s@%(address)s" % Xenadu.Env["Config"]["ssh"],
        command],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE).communicate()[0]

    logging.getLogger("Xenadu").debug("ssh returned:" + output)
    return output

def register():
	Xenadu.Env["Registry"].register_task(name="ssh.bootstrap", args=0, help="copy ssh config for the first time", function=ssh_bootstrap)
