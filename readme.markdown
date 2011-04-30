Xenadu is a tool for remotely managing system configurations, making it possible to keep track of configurations using a version control tool like git.  Once your system configuration is managed by Xenadu, it is easy to crank out clone machines.

So let's say you want to use Xenadu to manage a machine on your network named "augusta".

0. Install xenadu

```
wget github.com/iandennismiller/xenadu/blah.tgz
tar xvfz xenadu*.tgz
cd xenadu*
python setup.py install
```

1. Make a directory to store your configuration

```
mkdir -p augusta/files
```

2. Create a host definition file named augusta.py

```
touch augusta/augusta.py
chmod 755 augusta/augusta.py
```

3. Edit augusta.py, and paste this skeletal host definition file:

```
#!/usr/bin/env python

from Xenadu import XenaduConfig, Perm, f
import Xenadu

env = { 'ssh': { "user": "root", "address": "SKELETON" } }

class xenadu_instance(XenaduConfig):
    def file_list(self):
        mapping = [
            ['/etc/hosts', "hosts", Perm.root_644],
            ]
        return mapping

xenadu_instance(env)
```

4. Set the `ssh['address']` to point to your machine

5. Edit `mapping` to list the files you want to track.  `mapping` is a python list, where each item in the list represents one file on the remote host.  An item like `['/etc/hosts', "hosts", Perm.root_644]`consists of 3 values: 

- the complete path of the file on the remote host (`/etc/hosts`)
- the filename as it is locally stored (`hosts`)
- the permissions that file should have on the remote host (here, owner is `root` and permission is `644`).

6. Grab all of those files from the remote host:

```
./augusta.py --grab-all
```

7. The files are in ./files - that's it!  Save this configuration!

`git init; git commit -m 'initial xenadu config'`

