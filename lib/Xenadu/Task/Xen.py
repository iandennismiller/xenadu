import Xenadu
from Xenadu.Task.Ssh import ssh

def xen_create_image(dummy):
    xen_tools_cmd = "/usr/bin/xen-create-image --hostname=%(hostname)s --ip=%(ip)s --output=/etc/xen/domains --no-hosts " + \
        "--swap=%(swap)sMb --memory=%(ram)sMb --size=%(disk)sMb --verbose --force"
    ssh(xen_tools_cmd % Xenadu.Env["Config"]["xen"])
    
    set_auto_cmd = "ln -s /etc/xen/domains/%(hostname)s.cfg /etc/xen/auto" % Xenadu.Env["Config"]["xen"]
    ssh(set_auto_cmd)

def register():
	Xenadu.Env["Registry"].register_task(name="guest.create", args=0, help="create xen guest", function=xen_create_image)
