#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement  # needed for python 2.5
from fabric.api import *

# globals
env.project_name = 'odin'

# environments

def staging():
    "Use the actual webserver"
    env.hosts = ['192.168.1.18']
    env.user = 'root'
    env.path = '/opt/apps/%(project_name)s' % env
    env.virtualhost_path = env.path
    env.branch = 'master'

def production():
    "Use the actual webserver"
    env.hosts = ['114.215.101.7']
    env.user = 'root'
    env.path = '/opt/apps/%(project_name)s' % env
    env.virtualhost_path = env.path
    env.branch = 'master'


def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[staging])
    require('path')

    sudo('mkdir -p %(path)s; chown %(user)s:%(user)s %(path)s;' %
         env, pty=True)
    with cd(env.path):
        run('virtualenv . --no-site-packages;' % env, pty=True)
        run('mkdir logs; chmod a+w logs; mkdir releases; mkdir shared; mkdir packages;' %
            env, pty=True)
        run('cd releases; ln -s . current; ln -s . previous;', pty=True)
    
def deploy():
    """
    Deploy the latest version of the site to the servers,
    install any required third party modules,
    install the virtual host and then restart the webserver
    """
    require('hosts', provided_by=[staging])
    require('path')
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    upload_tar_from_git()
    install_requirements()
    symlink_current_release()
    restart_webserver()

def upload_tar_from_git():
    "Create an archive from the current Git master branch and upload it"
    require('release', provided_by=[deploy, setup])
    local('git archive --format=tar %(branch)s | gzip > %(release)s.tar.gz' %
          env)
    run('mkdir -p %(path)s/releases/%(release)s' % env, pty=True)
    put('%(release)s.tar.gz' % env, '%(path)s/packages/' % env)
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' %
        env, pty=True)
    local('rm %(release)s.tar.gz' % env)

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    run('cd %(path)s; ./bin/pip install  -r ./releases/%(release)s/requirements.txt' %
        env, pty=True)

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    with cd(env.path):
        run('rm releases/previous; mv releases/current releases/previous;')
        run('ln -s %(release)s releases/current' % env)
        with cd('releases/%(release)s' % env):
            run('ln -s %(path)s/logs ./logs' % env)

def restart_webserver():
    "Restart the web server"
    sudo('supervisorctl restart odin', pty=True)
    sudo('supervisorctl restart odin-admin', pty=True)