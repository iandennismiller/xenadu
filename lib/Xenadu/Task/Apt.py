import Xenadu
from Xenadu.Task.Ssh import ssh

def aptitude(dummy):
    apt_cmd = "aptitude -y install "
    for pkg in Xenadu.Env['Config']["apt"]:
        apt_cmd += "%s " % pkg
    
    ssh(apt_cmd)

def register():
    Xenadu.Env["Registry"].register_task(name="apt", args=0, help="aptitude install", function=aptitude)
