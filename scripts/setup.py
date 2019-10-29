#!/usr/bin/env python3

import os
import sys
import configparser
import subprocess
import re
import argparse

scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
configFile = scriptDir + '/' + 'config.ini'
config = configparser.ConfigParser()

config.read(configFile)

branch = config['base']['branch']

nocturneDir = os.path.abspath(os.path.dirname(scriptDir))
print(nocturneDir)


def checkout(directory, remote, branch, commit):
    cmd = "git clone {} {}".format(remote, directory)
    subprocess.check_call(cmd, shell=True)

    os.chdir(directory)

    cmd = "git checkout -b {} {}".format(branch + '-' + commit[0:5], commit)
    subprocess.check_call(cmd, shell=True)

def checkout_project(project):
    checkout(config[project]['name'],
             config[project]['remote'],
             config[project]['branch'],
             config[project]['commit'])

def checkout_projects():
    projects = config['base']['projects']
    projects = projects.split()

    os.chdir(nocturneDir)
    checkout_project("openembedded-core")

    # openembedded-core project is special because it is parent directory of other projects.
    projects.remove("openembedded-core")

    oecoreDir = nocturneDir + '/' + config['openembedded-core']['name']
    print(oecoreDir)
    for proj in projects:
        os.chdir(oecoreDir)
        checkout_project(proj)

def setup_templateconf():
    os.chdir(nocturneDir)
    import shutil
    shutil.copy(nocturneDir + "/scripts/templateconf", nocturneDir + "/oe-core/.templateconf")

if __name__ == '__main__':
    checkout_projects()
    setup_templateconf()
    print("nocturne linux branch {0} checked out.\n"
           "run 'cd oe-core' and '. oe-init-build-env build-{0}' and enjoy".format(config['base']['branch']))
