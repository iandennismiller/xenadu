Introduction
Start by installing Debian. If possible, use the USB boot method.

Next, install sudo and openssh

apt-get install sudo openssh-server rsync

Then, get ssh public key login working.

Resize the root partition
Boot in rescue mode

Before mounting the root disk, switch to a different terminal and execute:

fsck.ext3 -f /dev/debian/root resize2fs -f /dev/debian/root 4G lvresize -L4G /dev/debian/root reboot
Install the base Xenadu system
export XENADU_PATH = ~/Code/saperea/domination xenadu --config $XENADU_PATH/xenadu/dom0_compaq/dom0.py --simulate xenadu --config $XENADU_PATH/xenadu/dom0_compaq/dom0.py --deploy

Install a guest
xenadu --config $XENADU_PATH/xenadu/svn/svn.py --simulate
