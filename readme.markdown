# Xenadu

Xenadu is a tool for remotely managing system configurations, making it possible to keep track of configurations using a version control tool like git.  Once your system configuration is managed by Xenadu, it is easy to crank out clone machines.

## Getting started

So let's say you want to use Xenadu to manage a machine on your network named "davidbowie".

0. Install Xenadu on something other than your target machine (like your laptop):

    ```
    curl -L https://github.com/iandennismiller/xenadu/tarball/master -o xenadu.tgz
    tar xvfz xenadu.tgz
    cd iandennismiller-xenadu*
    python setup.py install
    ```

1. Make a directory to store your configuration (we'll call it davidbowie, since that's the name of the machine).  The `files` subdirectory will contain a copy of all the remotely managed files.

    ```
    mkdir davidbowie
    cd davidbowie
    mkdir files
    ```

2. Create a host definition file named `davidbowie.py` (or whatever you want, but again since this machine is named davidbowie, that's what I'm calling it)

    ```
    touch ./davidbowie.py
    chmod 755 ./davidbowie.py
    ```

3. Edit davidbowie.py, and paste this skeletal host definition file:

    ```python
    #!/usr/bin/env python
    from Xenadu import XenaduConfig, Perm
    mapping = [
        ['/etc/hosts', "hosts", Perm.root_644],
        ['/etc/network/interfaces', "interfaces", Perm.root_644],
        ]
    env = { 'ssh': { "user": "root", "address": "SKELETON" } }
    XenaduConfig(env, mapping)
    ```

4. Set the `ssh['address']` to point to your machine.

    ```python
    env = { 'ssh': { "user": "root", "address": "somewhere.example.com" } }
    ```

    Also, make sure you are familiar with ssh public key authentication.  You need to log in as root in order for Xenadu to function correctly.  If you are uncomfortable with being able to log in as root, then make sure your private key is password-protected, and use a ssh keychain manager.

5. Edit `mapping` to list the files you want to track.  `mapping` is a python list, where each item in the list represents one file on the remote host.  An item like `['/etc/network/interfaces', "interfaces", Perm.root_644]` consists of 3 values: 

    - `/etc/network/interfaces` is the complete path of the file on the remote host
    - `interfaces` is the local name of the file, which is in the `./files` directory.
    - `Perm.root_644` is the permissions that file should have on the remote host (here, owner is `root` and permission is `644`).

6. Grab all of those files from the remote host:

    ```
    ./davidbowie.py --getall
    ```

    This will automatically go through every item in `mapping` and download it to the local `./files` directory.

7. The files are in `./files` - save this configuration!

    ```
    git init; git commit -m 'initial davidbowie config'
    ```

## Deploying changes

So let's say you edit `./files/interfaces` and you want to push this to the remote machine.  This is way easier with Xenadu than manually copying the file with SSH, which requires you to type out the hostname and the paths for the local and remote files.  

```
./davidbowie.py --push interfaces
```

Or, if you forget what you call the file locally but remember the remote name, use that:

```
./davidbowie.py --push /etc/network/interfaces
```

You'll probably end up learning to use the shorter version for files you commonly deal with.  

## Permissions

In the "Getting started" example, `/etc/network/interfaces` uses `Perm.root_644` to set its permissions to a fairly standard level.  What about a file like `/etc/sudoers`, which needs stricter permissions?  It's pretty easy to create new permission schemes:

```python
# make a new permission
sudoers_perm = {"perm": "0440", "owner": "root", "group": "root"}

# use it as you append the sudoers file to the mapping
mapping.append(['/etc/sudoers', 'sudoers', sudoers_perm])
```

You could even go so far as to do something like:

```python
mapping.append(['/etc/sudoers', 'sudoers', {"perm": "0440", "owner": "root", "group": "root"}])
```

In fact, `Perm.root_644` is just a convenient equivalent to `{"perm": "0644", "owner": "root", "group": "root"}`, so that's what it actually means when you say something like `['/etc/hosts', "hosts", Perm.root_644]`.

## Multiple systems using a single definition file

In web app development, it's pretty common to have a staging server that is almost identical to the production server.  With Xenadu, it's pretty easy to use a single definition file to control both the staging and production servers.  Here is a quick example of what you can put at the end of your definition file, right before the `XenaduConfig(env, mapping)` directive:

```python
if 'XENADU' in os.environ and os.environ['XENADU'] == 'dev':
    env['ssh']['address'] = "dev.example.com"
    custom_dev_files = [
        ['/etc/network/interfaces', "interfaces-dev", Perm.root_644],
    ]
    mapping.extend(custom_dev_files)
XenaduConfig(env, mapping)
```

Now putting `XENADU=dev` before your command will push the development version of `/etc/network/interfaces` to `dev.example.com`:

```
XENADU=dev ./davidbowie.py --push /etc/network/interfaces
```

This is useful because it lets you keep a single version control repository with all of the files for your stage and production server in one place.
