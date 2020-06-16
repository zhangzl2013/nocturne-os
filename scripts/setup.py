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

def shell(cmd):
    try:
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def checkout(directory, remote, branch, commit):
    ret = True
    # save current working directory
    saved_cwd = os.getcwd()

    if os.path.isdir(directory):
        print("directory {} exists, skip cloning".format(directory))
    else:
        shell("git clone {} {}".format(remote, directory))

    os.chdir(directory)

    if shell("git diff-index --quiet HEAD --"):
        branch_name = branch + '-' + commit[0:6] if commit else branch
        # if branch_name exists
        if shell("git branch --list {0} | grep --quiet {0}".format(branch_name)):
            shell("git checkout {}".format(branch_name))
        else:
            shell("git checkout -b {} {}".format(branch_name, commit))

    else:
        print("Warning: directory {} not clean.\n"
              "Please save uncommitted changes and rerun this script.".format(directory))
        ret = False

    # restore working directory
    os.chdir(saved_cwd)
    return ret


def checkout_project(project):
    if not checkout(config[project]['name'],
                    config[project]['remote'],
                    config[project]['branch'],
                    config[project]['commit']):
        raise UserWarning

def checkout_projects():
    rev = True
    projects = config['base']['projects']
    projects = projects.split()

    # openembedded-core project is special because it is parent directory of other projects.
    projects.remove("openembedded-core")

    try:
        os.chdir(nocturneDir)
        checkout_project("openembedded-core")
    except UserWarning:
        # set rev to False but continue to check other projects
        rev = False

    oecoreDir = nocturneDir + '/' + config['openembedded-core']['name']

    os.chdir(oecoreDir)
    for proj in projects:
        try:
            checkout_project(proj)
        except UserWarning:
            # set rev to False but continue to check other projects
            rev = False


    return rev

def setup_templateconf():
    saved_cwd = os.getcwd()

    os.chdir(nocturneDir)
    import shutil
    shutil.copy(nocturneDir + "/scripts/templateconf", nocturneDir + "/oe-core/.templateconf")

    # change in .templateconf is never saved.
    # 'git stash' make the working directory look clean.
    shell("git stash")

    os.chdir(saved_cwd)

if __name__ == '__main__':
    if not checkout_projects():
        sys.exit(1)

    setup_templateconf()
    print("nocturne linux branch {0} checked out.\n"
           "run 'cd oe-core' and '. oe-init-build-env build-{0}' and enjoy".format(config['base']['branch']))

    sys.exit(0)
