from fabric.api import env, run, local, hosts, put, settings
import os, sys, glob

def xenadu(action='simulate'):
    """
    call xenadu with an action (simulate, deploy, apt, guest.create...)
    """
    cmd = "xenadu --config %s --%s" % (env.cfg, action)
    local(cmd, capture=False)

def prime_ssh(lvm_path=''):
    """
    Prime a freshly created (unbooted) guest with existing ssh server keys and a root auth
    """
    if not lvm_path:
        return
    
    ssh_path = '/Users/idm/Code/saperea/domination/xenadu/svn/files/_ssh'
    root_authorized_keys2 = '/Users/idm/Code/saperea/domination/xenadu/_common/_ssh/authorized_keys2-root'

    run("umount /mnt/xenadu; mount %s /mnt/xenadu" % lvm_path)
    put(os.path.join(ssh_path, "ssh_host_dsa_key"), "/mnt/xenadu/etc/ssh/ssh_host_dsa_key", mode=0600)
    put(os.path.join(ssh_path, "ssh_host_dsa_key.pub"), "/mnt/xenadu/etc/ssh/ssh_host_dsa_key.pub", mode=0644)
    put(os.path.join(ssh_path, "ssh_host_rsa_key"), "/mnt/xenadu/etc/ssh/ssh_host_rsa_key", mode=0600)
    put(os.path.join(ssh_path, "ssh_host_rsa_key.pub"), "/mnt/xenadu/etc/ssh/ssh_host_rsa_key.pub", mode=0644)
    run("mkdir -p /mnt/xenadu/root/.ssh")
    put(root_authorized_keys2, "/mnt/xenadu/root/.ssh/authorized_keys2", mode=0644)
    run("umount /mnt/xenadu")

def start():
    """
    start the xen domain
    """
    run("xm create /etc/xen/domains/%s.cfg" % env.lvm_base)

def stop():
    """
    stop the xen domain
    """
    run("xm shutdown %s" % env.lvm_base)

def console():
    """
    view the console of this xen domain
    """
    run("xm console %s" % env.lvm_base)

def list():
    """
    list running xen domains
    """
    run("xm list")

def setup_lvm(size='5G'):
    """
    create an LVM partition for holding data
    """
    c = {
        'size': size,
        'lvm_base': env.lvm_base,
        'pv_dev': env.pv_dev,
    }
    
    cmd = """
    lvcreate -L%(size)s -n %(lvm_base)s-data %(pv_dev)s;
    mke2fs -j %(pv_dev)s/%(lvm_base)s-data
    """ % c
    run(cmd)
    
def run_in_volume(lvm_path='', cmd=''):
    """
    run a command inside a mounted lvm volume
    """
    if not cmd:
        return
    run("umount /mnt/xenadu; mount %s /mnt/xenadu" % lvm_path)
    run(cmd)
    run("umount /mnt/xenadu")

def setup_backuppc():
    """
    set up backuppc login
    """

    auth_file = "/Users/idm/Code/saperea/domination/xenadu/_common/authorized_keys2-backuppc"
    cmd = """
    groupadd backuppc;
    useradd -c "BackupPC User" -d /home/backuppc -m -g backuppc -s /bin/rbash backuppc;
    mkdir /home/backuppc/.ssh
    """
    run(cmd)
    put(auth_file, "/home/backuppc/.ssh/authorized_keys2")
    run("chown -R backuppc:backuppc /home/backuppc")

def setup_idm():
    """
    setup idm login
    """
    auth_file = "/Users/idm/Code/saperea/domination/xenadu/_common/authorized_keys2-idm"
    cmd = """
    useradd -c "idm" -d /home/idm -m -s /bin/bash idm;
    mkdir -p /home/idm/.ssh;
    """
    run(cmd)
    put(auth_file, "/home/idm/.ssh/authorized_keys2")
    run("chown -R idm:idm /home/idm")

def image_receive(device=''):
    """
    start netcat server, receive a disk image
    """
    if not device:
        return
    #cmd = "nc -l -p 19000|bzip2 -d|dd bs=16M of=%s" % device
    cmd = "nc -l -p 19000 | dd bs=16M of=%s" % device
    run(cmd)
    
def image_send(device='', dest=''):
    """
    send a disk image using netcat
    """
    if not device:
        return
    if not dest:
        return
    #cmd = "dd bs=16M if=%s |bzip2 -c | nc %s 19000" % (device, dest)
    cmd = "dd bs=16M if=%s | nc %s 19000" % (device, dest)
    run(cmd)

def image_resize(lvm_path='', size=''):
    """
    resize a remote disk image
    """
    c = {
        'lvm_path': lvm_path, 
        'size': size
    }
    cmd = "e2fsck -f -a %(lvm_path)s; resize2fs %(lvm_path)s %(size)s" % c
    run(cmd)

def send_fstab(lvm_dev=''):
    """
    copy the fstab onto an unbooted image
    """
    if not lvm_dev:
        return
    run("umount /mnt/xenadu; mount %s /mnt/xenadu" % lvm_dev)
    put('files/fstab', '/mnt/xenadu/etc/fstab', mode=0644)
    run("umount /mnt/xenadu")

def migrate_image(from_dom0, from_lvm, to_ip, new_size='5G'):
    """
    migrate an lvm image from one unbooted guest to another
    """
    c = {
        'from_dom0': from_dom0,
        'from_lvm': from_lvm,
        'to_ip': to_ip,
        'dom0': env.dom0,
        'pv_dev': env.pv_dev,
        'lvm_base': env.lvm_base,
        'size': new_size
    }
    
    cmd = """
    fab -H %(dom0)s image_receive:%(pv_dev)s/%(lvm_base)s-data
    fab -H %(from_dom0)s image_send:%(from_lvm)s,%(to_ip)s
    fab -H %(dom0)s image_resize:%(pv_dev)s/%(lvm_base)s-data,%(size)s
    fab -H %(dom0)s start
    """ % c
    print cmd

def install_finish():
    """
    finish xenadu guest installation
    """
    #ssh root@%(hostname)s ln -s /mnt/maildir /var/Maildir

    xenadu('apt')
    xenadu('deploy')
    
    with settings(host_string=env.lvm_base):
        setup_idm()

def install_start():
    """
    begin installing xenadu guest
    """
    xenadu('guest.create')

    with settings(host_string=env.dom0):
        prime_ssh("%(pv_dev)s/%(lvm_base)s-disk" % env)
        setup_lvm("5G")
        run_in_volume("%(pv_dev)s/%(lvm_base)s-disk" % env, 'mkdir /mnt/xenadu/mnt/data')
        send_fstab("%(pv_dev)s/%(lvm_base)s-disk" % env)

def migration():
    """
    migrate a machine from one host to another
    """
    install_start()
    a = raw_input('start migration?')
    migrate_image('domination','/dev/dom0/highriseweb.saperea.com-data','192.168.9.1')
    a = raw_input('has migration completed?')
    os.system('rsync dom0/xen.cfg root@augusta:/etc/xen/domains/highriseweb.saperea.com.cfg')
    install_finish()

def setup_user(username=''):
    """
    setup user
    """
    if not username:
        return

    auth_file = "/Users/idm/Code/saperea/domination/xenadu/_common/authorized_keys2-idm"

    cmd = """
    useradd -c "%(username)s" -d /home/%(username)s -m -s /bin/bash %(username)s;
    mkdir -p /home/%(username)s/.ssh;
    """ % {'username': username}

    run(cmd)
    put(auth_file, "/home/%s/.ssh/authorized_keys2" % username)
    run("chown -R %s:%s /home/%s" % (username, username, username))

def easy_install():
    """
    install python easy_install
    """
    cmd = """wget http://peak.telecommunity.com/dist/ez_setup.py
    python ez_setup.py
    easy_install virtualenv
    """
    run(cmd)

def mod_wsgi(version='3.1'):
    """
    install mod_wsgi
    """
    def install_tgz(url, app, version):
        cmd = """
        cd /tmp;
        wget -O /tmp/%(app)s.tar.gz %(url)s;
        tar xvfz /tmp/%(app)s.tar.gz;
        cd %(app)s-%(version)s;
        ./configure;
        make;
        make install;
        """ % {'version': version, 'app': app, 'url': url}
        return cmd % {'version': version}

    cmd = install_tgz('http://modwsgi.googlecode.com/files/mod_wsgi-%(version)s.tar.gz', 'mod_wsgi', version)
    run(cmd)

    cmd = "echo 'LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so' > /etc/apache2/mods-available/wsgi.load;" 
    cmd += "a2enmod wsgi; /etc/init.d/apache2 restart"
    run(cmd)
