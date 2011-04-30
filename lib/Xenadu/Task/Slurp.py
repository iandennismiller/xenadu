import Xenadu
import os, shutil, subprocess, string, re, sys, logging

def slurp_remote(remote_file, file_mapping=None):
    entry = None
    try:
        entry = Xenadu.Env["Config"]["mapping"][remote_file]
    except:
        for filename in Xenadu.Env["Config"]["mapping"]:
            if Xenadu.Env["Config"]["mapping"][filename]['local_file'] == remote_file:
                entry = Xenadu.Env["Config"]["mapping"][filename]

    if not entry:
        logging.getLogger("Xenadu").error("can't find: %s" % remote_file)
        return

    local_file = os.path.join(Xenadu.Env["Config"]["guest_path"], "files", entry['local_file'])
    remote_file = os.path.join(Xenadu.Env["Config"]["guest_path"], "files", entry['remote_file'])

    logging.getLogger("Xenadu").info("get remote file: %s" % remote_file)
    logging.getLogger("Xenadu").info("to local file: %s" % local_file)
    ssh = Xenadu.Env["Config"]["ssh"]
    cmd = '/usr/bin/scp "%s@%s:%s" "%s"' % (ssh["user"], ssh["address"], remote_file, local_file)
    os.system(cmd)
    #subprocess.Popen(["/usr/bin/scp", "%s@%s:%s" % (ssh["user"], ssh["address"], remote_file), local_file])

def push_remote(remote_file, file_mapping=None):
    entry = None
    try:
        entry = Xenadu.Env["Config"]["mapping"][remote_file]
    except:
        for filename in Xenadu.Env["Config"]["mapping"]:
            if Xenadu.Env["Config"]["mapping"][filename]['local_file'] == remote_file:
                entry = Xenadu.Env["Config"]["mapping"][filename]
    
    if not entry:
        logging.getLogger("Xenadu").error("can't find: %s" % remote_file)
        return

    h = {
        'local': os.path.join(Xenadu.Env["Config"]["guest_path"], "files", entry['local_file']),
        'remote': os.path.join(Xenadu.Env["Config"]["guest_path"], "files", entry['remote_file']),
        'user': Xenadu.Env["Config"]["ssh"]['user'],
        'address': Xenadu.Env["Config"]["ssh"]['address'],
        'owner': entry['owner'],
        'group': entry['group'],
        'perm': entry['perm'],
    }

    logging.getLogger("Xenadu").info("push local file: %(local)s to remote file: %(remote)s" % h)
    cmd = '/usr/bin/scp "%(local)s" "%(user)s@%(address)s:%(remote)s"' % h
    os.system(cmd)
    h['subcmd'] = 'chown %(owner)s:%(group)s "%(remote)s"; chmod %(perm)s "%(remote)s"' % h
    cmd = "ssh %(user)s@%(address)s '%(subcmd)s'" % h
    os.system(cmd)

def slurp_local(filename, file_mapping = None):
    if file_mapping == None:
        file_mapping = Xenadu.Env["Config"]["mapping"]
    
    for key in file_mapping:
        entry = file_mapping[key]
        if entry["local_file"] == filename:
            slurp_remote(entry["remote_file"])
            return
    logging.getLogger("Xenadu").error("couldn't find a match for: %s" % filename)

def slurp_all(dummy, file_mapping = None):
    if file_mapping == None:
        file_mapping = Xenadu.Env["Config"]["mapping"]
    for filename in file_mapping:
        slurp_remote(filename)

def diff(remote_file, file_mapping=None):
    try:
        entry = Xenadu.Env["Config"]["mapping"][remote_file]
    except:
        logging.getLogger("Xenadu").error("can't find: %s" % remote_file)
        return

    local_file = os.path.join(Xenadu.Env["Config"]["guest_path"], "files", entry['local_file'])
    logging.getLogger("Xenadu").info("diff remote file: %s, local file: %s" % (remote_file, local_file))
    ssh = Xenadu.Env["Config"]["ssh"]
    cmd = '/usr/bin/scp "%s@%s:%s" /tmp/xenadu/diff.txt' % (ssh["user"], ssh["address"], remote_file)
    os.system(cmd)
    os.system("diff -c /tmp/xenadu/diff.txt %s" % local_file)

def register():
    #Xenadu.Env["Registry"].register_task(name="local", args=1, help="copy file from remote host based on local filename", function=slurp_local)
    #Xenadu.Env["Registry"].register_task(name="remote", args=1, help="copy file based on remote filename", function=slurp_remote)
    Xenadu.Env["Registry"].register_task(name="getall", args=0, help="copy all files from remote host", function=slurp_all)
    Xenadu.Env["Registry"].register_task(name="diff", args=1, help="diff remote file with local version", function=diff)
    Xenadu.Env["Registry"].register_task(name="push", args=1, help="push local file to remote host", function=push_remote)
    Xenadu.Env["Registry"].register_task(name="get", args=1, help="get a file from remote host", function=slurp_remote)
