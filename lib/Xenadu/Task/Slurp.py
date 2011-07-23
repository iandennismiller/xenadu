import Xenadu
import os, shutil, subprocess, string, re, sys, logging

def cp_remote(filename, file_mapping=None, direction=None):
    h = Xenadu.Env['Mapping'].resolve_name(filename)
    h['user'] = Xenadu.Env["Config"]["ssh"]['user']
    h['address'] = Xenadu.Env["Config"]["ssh"]['address']

    if direction == 'push':
        logging.getLogger("Xenadu").info("push local file: %(local_file)s to remote file: %(remote_file)s" % h)
        cmd = '/usr/bin/scp "%(local_file)s" "%(user)s@%(address)s:%(remote_file)s"' % h
        os.system(cmd)
        h['subcmd'] = 'chown %(owner)s:%(group)s "%(remote_file)s"; chmod %(perm)s "%(remote_file)s"' % h
        cmd = "ssh %(user)s@%(address)s '%(subcmd)s'" % h
        os.system(cmd)    
    elif direction == 'get':
        logging.getLogger("Xenadu").info("get remote file: %(remote_file)s to local file: %(local_file)s" % h)
        cmd = '/usr/bin/scp "%(user)s@%(address)s:%(remote_file)s" "%(local_file)s"' % h
        os.system(cmd)

def slurp_remote(remote_file, file_mapping=None):
    cp_remote(remote_file, file_mapping, 'get')

def push_remote(remote_file, file_mapping=None):
    cp_remote(remote_file, file_mapping, 'push')

def slurp_all(dummy, file_mapping = None):
    if file_mapping == None:
        file_mapping = Xenadu.Env["Config"]["mapping"]
    for filename in file_mapping:
        slurp_remote(filename)

def diff(filename, file_mapping=None):
    entry = Xenadu.Env['Mapping'].resolve_name(filename)
    logging.getLogger("Xenadu").info("diff remote file: %(remote_file)s, local file: %(local_file)s" % entry)
    ssh = Xenadu.Env["Config"]["ssh"]
    cmd = '/usr/bin/scp "%s@%s:%s" /tmp/xenadu_diff.txt' % (ssh["user"], ssh["address"], entry['remote_file'])
    os.system(cmd)
    os.system("diff -c /tmp/xenadu_diff.txt %s" % entry['local_file'])

def register():
    Xenadu.Env["Registry"].register_task(name="getall", args=0, help="copy all files from remote host", function=slurp_all)
    Xenadu.Env["Registry"].register_task(name="diff", args=1, help="diff remote file with local version", function=diff)
    Xenadu.Env["Registry"].register_task(name="push", args=1, help="push local file to remote host", function=push_remote)
    Xenadu.Env["Registry"].register_task(name="get", args=1, help="get a file from remote host", function=slurp_remote)
