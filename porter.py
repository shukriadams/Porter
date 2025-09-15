# porter install --path /some/path
import argparse
import os
import sys
import json
import re as regex
import shutil
import subprocess
import glob
import codecs

class Package:
    def __init__(self, repo, tag):
        self.Source = 'https://github.com' # currently only public github repos supported
        self.Repo = repo.replace('.', '/') # github repos dont have .'s, must be /
        self.Tag = tag # current only only tag is supported

def exec(command, cwd=None):

    # force to run in current dir if none set
    if cwd is None:
        cwd = os.path.dirname(os.path.realpath(__file__))

    result = subprocess.Popen(command,
        cwd=cwd,
        shell=True, 
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)

    # wait for command to exit. NOTE : this is extremely likely to hang, rewrite to use .communicate() instead
    result.wait()

    returnCode = result.poll()

    # if fail to get a return code from poll, assume pass, this is probably not a good idea but not 
    # sure how else to handle this now. Ideally wait should always be on
    if returnCode is None:
        returnCode = 0

    stdout = result.stdout.readlines()
    stderr = result.stderr.readlines()

    # convert to
    for i in range(0, len(stdout)):
        stdout[i] = stdout[i].decode('utf-8')

    for i in range(0, len(stderr)):
        stderr[i] = stderr[i].decode('utf-8')

    if returnCode != 0:
        print (f'ERROR : command \"{command}\" failed, return code was {returnCode}, error was :')
        print(stderr)
        sys.exit(1)

    return returnCode


def process_porter(root_dir_path, context=[]):
    porter_start_file_path = os.path.join(root_dir_path, 'porter.json')
    if not os.path.isfile(porter_start_file_path):
        print(f'Error : expected porter.json not found at path {root_dir_path}, ignoring')
        return

    porter_conf = {}
    porter_packages_dir = os.path.join(root_dir_path, 'porter')

    try:
        with open(porter_start_file_path) as file:
            porter_conf = json.load(file)
    except Exception as e:
        print(f'Error : loading json from {porter_start_file_path}:{e}')
        sys.exit(1)

    packages_to_install = []
    package_name=porter_conf['name']
    
    context = context[:]
    context.append(package_name)

    print(f'!! PORTER processing path {root_dir_path}, context is {context}')

    # generate package to install from conf packages
    for package in porter_conf['packages']:
        src = package['source']
        if package['source'] != 'github':
            print(f'Error : only github currently supported : {src}') 
            sys.exit(1)

        p = Package(package['repo'], package['tag'])
        packages_to_install.append(p)

    for package in packages_to_install:
        print(package.Repo)
        occurences = [i for i, x in enumerate(packages_to_install) if x.Repo == package.Repo]
        if len(occurences) > 1:
            print(f'Error : package {package.Repo} occurs more than once')
            sys.exit(1)

    if not os.path.isdir(porter_packages_dir):
        os.makedirs(porter_packages_dir)

    destructive=True

    for package in packages_to_install:
        package_dir = os.path.join(porter_packages_dir, package.Repo)
        if destructive and os.path.isdir(package_dir):
            shutil.rmtree(package_dir)   

        if not os.path.isdir(package_dir):
            os.makedirs(package_dir)
            result = exec(f'git clone --branch {package.Tag} {package.Source}/{package.Repo} {package_dir}')
            if result != 0:
                sys.exit(0)
        
        package_porter_conf = os.path.join(package_dir, 'porter.json')
        isPackagePorter=True
        if not os.path.isfile(package_porter_conf):
            print(f'Warning : package @ path {package_porter_conf} is not a porter package')
            isPackagePorter=False        

        # delete .git dir
        git_dir = os.path.join(package_dir, '.git')
        if os.path.isdir(git_dir):
            shutil.rmtree(git_dir)

        # wrap all cs files
        cs_files = glob.glob(os.path.join(package_dir, '**.cs')) # not sure this will work on nested
        for cs_file in cs_files:
            with codecs.open(cs_file, encoding='utf-8') as file:
                file_content = file.read()
                if ('//PORTER-WRAPPER' in file_content):
                    continue

                namespace_lead = '//PORTER-WRAPPER!\n'
                namespace_tail= ''
                for this_context in context:
                    namespace_lead = (namespace_lead+
                        'namespace '+this_context+'.Porter_Packages {\n')

                    namespace_tail = namespace_tail +'}\n'

                namespace_lead = f'{namespace_lead}//PORTER-WRAPPER!\n\n\n'
                namespace_tail = f'\n\n//PORTER-WRAPPER!\n{namespace_tail}//PORTER-WRAPPER!'


                file_content = f'{namespace_lead}{file_content}{namespace_tail}'

                with open(cs_file, 'w') as output:
                    output.write(file_content)
                    print(f'wrapped file {cs_file}')

        if isPackagePorter:
            process_porter(package_dir, context)   



argsParser = argparse.ArgumentParser()
argsParser.add_argument('--install', action='store_true')
argsParser.add_argument('--path', default=None)
args = argsParser.parse_args()

if args.install and args.path is None:
    print('Error : --path required for install')
    sys.exit(1)

if args.install:
    print(f'install to {args.path}')

root_dir_path = os.path.abspath(args.path)

porter_start_file_path = os.path.join(root_dir_path, 'porter.json')
if not os.path.isfile(porter_start_file_path):
    print(f'Error : expected porter.json not found at path {root_dir_path}')
    sys.exit(1)

process_porter(root_dir_path)
