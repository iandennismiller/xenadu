import Xenadu, logging
from Xenadu.Task.Ssh import ssh

def aptitude(dummy):
    if "apt" not in Xenadu.Env:
        logging.getLogger("Xenadu").error("host definition has no apt=blah?")
        return

    apt_cmd = "export DEBIAN_FRONTEND=noninteractive; aptitude -y install "
    for pkg in Xenadu.Env["apt"]:
        apt_cmd += "%s " % pkg    
    ssh(apt_cmd)

def register():
    Xenadu.Env["Registry"].register_task(name="apt", args=0, help="aptitude install", function=aptitude)
