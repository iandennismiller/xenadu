import sys, os
from fabric.api import env, local

def sphinx():
    cmd = """
    cd sphinx
    rm -rf /tmp/api
    sphinx-build -b html . /tmp/api
    rsync -a /tmp/api $RSYNC_AUTH
    rm -rf /tmp/api
    cd ..
    """

def sdist():
    print local('cp wiki/ReadMe.wiki doc/README.txt')
    #print local('cp wiki/InstallWindows.wiki doc/INSTALL-WIN.TXT')
    #print local('cp wiki/InstallUnix.wiki doc/INSTALL-UNIX.TXT')
    print local('rm -rf build; python setup.py sdist --formats=zip,gztar')

def tag():
    ver = local('python setup.py --version').rstrip()
    cmd = 'svn cp https://xenadu.googlecode.com/svn/trunk/ https://xenadu.googlecode.com/svn/tags/%s/'
    os.system(cmd % ver)

def test():
    cmd = 'nosetests -v t/test_fft_data.py'
    os.system(cmd)
