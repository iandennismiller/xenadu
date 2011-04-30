# Xenadu

Xenadu is a tool for remotely managing system configurations, making it possible to keep track of configurations using a version control tool like git.  Once your system configuration is managed by Xenadu, it is easy to crank out clone machines.

## Getting started

So let's say you want to use Xenadu to manage a machine on your network named "augusta".

0. Install xenadu

    ```
    curl -L https://github.com/iandennismiller/xenadu/tarball/master -o xenadu.tgz
    tar xvfz xenadu.tgz
    cd iandennismiller-xenadu*
    python setup.py install
    ```

1. Make a directory to store your configuration (we'll call it augusta, since that's the name of the machine)

    ```
    mkdir -p augusta/files
    ```

2. Create a host definition file named augusta.py

    ```
    cd augusta
    touch augusta.py
    chmod 755 augusta.py
    ```

3. Edit augusta.py, and paste this skeletal host definition file:

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

5. Edit `mapping` to list the files you want to track.  `mapping` is a python list, where each item in the list represents one file on the remote host.  An item like `['/etc/hosts', "hosts", Perm.root_644]` consists of 3 values: 

    - the complete path of the file on the remote host (`/etc/hosts`)
    - the filename as it is locally stored (`hosts`)
    - the permissions that file should have on the remote host (here, owner is `root` and permission is `644`).

    After adding another file, `mapping` might look like this:

    ```python
    mapping = [
        ['/etc/hosts', "hosts", Perm.root_644],
        ['/etc/network/interfaces', "interfaces", Perm.root_644],
        ['/etc/resolv.conf', "resolv.conf", Perm.root_644],
        ]
    ```

6. Grab all of those files from the remote host:

    ```
    ./augusta.py --getall
    ```

    This will automatically go through every item in `mapping` and download it to the local `./files` directory.

7. The files are in `augusta/files` - save this configuration!

    ```
    git init; git commit -m 'initial xenadu config'
    ```

## Deploying changes

So let's say you edit `augusta/files/hosts` and you want to push this to the remote machine.

```
./augusta.py --push hosts
```

Or, if you forget what you call the file locally but remember the remote name, use that:

```
./augusta.py --push /etc/hosts
```

## Permissions

In the "Getting started" example, `/etc/hosts` uses `Perm.root_644` to set its permissions to a fairly standard level.  What about a file like `/etc/sudoers`, which needs stricter permissions?  Luckily, it's pretty easy to create new permission schemes.  See the following example:

```python
sudoers_perm = {"perm": "0440", "owner": "root", "group": "root"}
mapping.append(['/etc/sudoers', 'sudoers', sudoers_perm])
```

In fact, `Perm.root_644` is equivalent to `{"perm": "0644", "owner": "root", "group": "root"}`, so really it's just there for convenience.

## Multiple systems using a single definition file

In web app development, it's pretty common to have a staging server that is almost identical to the production server.  With Xenadu, it's pretty easy to use a single definition file to control both the staging and production servers.  Here is a quick example of what you can put at the end of your definition file, right before the `XenaduConfig(env, mapping)` directive:

```
if 'XENADU' in os.environ and os.environ['XENADU'] == 'dev':
    env['ssh']['address'] = "dev.example.com"
    custom_dev_files = [
        ['/etc/hosts', "hosts-dev", Perm.root_644],
    ]
    mapping.extend(custom_dev_files)
    XenaduConfig(env, mapping)
```

Now putting `XENADU=dev` before your command will push the development version of `/etc/hosts` to `dev.example.com`:

```
XENADU=dev ./augusta.py --push /etc/hosts
```
