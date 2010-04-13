from Xenadu.Core import Core
import os, shutil, subprocess, string
#import Xenadu.Task.Sync
from Xenadu.Language import Language, file, common

def ssh_deploy_server_keys(dummy):
    Xenadu.Task.Build.clean(0)

    X = Language()
    X.add("/etc/ssh/ssh_host_dsa_key", file("_ssh/ssh_host_dsa_key"), X.root_600)
    X.add("/etc/ssh/ssh_host_dsa_key.pub", file("_ssh/ssh_host_dsa_key.pub"))
    X.add("/etc/ssh/ssh_host_rsa_key", file("_ssh/ssh_host_rsa_key"), X.root_600)
    X.add("/etc/ssh/ssh_host_rsa_key.pub", file("_ssh/ssh_host_rsa_key.pub"))
    mapping = X.get_hash()

    Xenadu.Task.Sync.do_build(mapping)

    output = subprocess.Popen(["/usr/bin/rsync", "-rpv", 
        "%s/build/" % Core.context.globals["tmp_path"],
        "%(user)s@%(address)s:/" % Core.config["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output

def ssh_bootstrap(dummy):
    Xenadu.Task.Build.clean(0)

    X = Language()
    X.add("/root/.ssh/authorized_keys2", file("_ssh/authorized_keys2-root"))
    X.add("/etc/ssh/sshd_config", file("_ssh/sshd_config"))
    mapping = X.get_hash()

    Xenadu.Task.Sync.do_build(mapping)

    output = subprocess.Popen(["/usr/bin/rsync", "-rpv", 
        "%s/build/" % Core.context.globals["tmp_path"], 
        "%(user)s@%(address)s:/" % Core.config["ssh"]],
        stdout=subprocess.PIPE).communicate()[0]
    print output

def ssh_import_server_keys(dummy):
    X = Language()
    X.add("/etc/ssh/ssh_host_dsa_key", file("_ssh/ssh_host_dsa_key"), X.root_600)
    X.add("/etc/ssh/ssh_host_dsa_key.pub", file("_ssh/ssh_host_dsa_key.pub"))
    X.add("/etc/ssh/ssh_host_rsa_key", file("_ssh/ssh_host_rsa_key"), X.root_600)
    X.add("/etc/ssh/ssh_host_rsa_key.pub", file("_ssh/ssh_host_rsa_key.pub"))
    mapping = X.get_hash()
    
    Xenadu.Task.Slurp.slurp_from("/etc/ssh/ssh_host_dsa_key", file_mapping = mapping)
    Xenadu.Task.Slurp.slurp_from("/etc/ssh/ssh_host_dsa_key.pub", file_mapping = mapping)
    Xenadu.Task.Slurp.slurp_from("/etc/ssh/ssh_host_rsa_key", file_mapping = mapping)
    Xenadu.Task.Slurp.slurp_from("/etc/ssh/ssh_host_rsa_key.pub", file_mapping = mapping)

def ssh_dom0(command):
    Core.logger.debug("ssh_dom0: " + command)
    
    output = subprocess.Popen(["/usr/bin/ssh",
        "%(user)s@%(address)s" % Core.config["dom0"]["ssh"],
        command],
        stdout=subprocess.PIPE).communicate()[0]

    Core.logger.debug("ssh_dom0 returned:" + output)
    return output

def ssh(command):
    Core.logger.debug("ssh_guest: " + command)

    output = subprocess.Popen(["/usr/bin/ssh",
        "%(user)s@%(address)s" % Core.config["ssh"],
        command],
        stdout=subprocess.PIPE).communicate()[0]

    Core.logger.debug("ssh_guest returned:" + output)
    return output

def register():
	Core.registry.register_task(name="ssh.bootstrap", args=0, help="copy ssh config for the first time", function=ssh_bootstrap)
	Core.registry.register_task(name="ssh.keys.deploy", args=0, help="copy ssh keys over", function=ssh_deploy_server_keys)
	Core.registry.register_task(name="ssh.keys.import", args=0, help="grab ssh keys from remote server", function=ssh_import_server_keys)
