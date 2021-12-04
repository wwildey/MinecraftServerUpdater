#!/usr/bin/env python

'''
Python script to update a minecraft server running on either Windows or Linux

This script is a modification of the script found at https://github.com/eclair4151/MinecraftUpdater 
and has been modified to run on both Windows and Linux platforms. 

Usage: (On Linux, this script can be made executable with command chmod +x <script name>)
    Linux:
        update_mc_server.py 
    Windows
        python update_mc_server.py
        
NOTE: Current settings assume that this script is placed in a sub-directory of the server,jar location

'''
import os
import sys
import time
import shutil
import hashlib
import time
from datetime import datetime
import logging
import requests
import platform

# Common config settings
UPDATE_TO_SNAPSHOT = False
MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
LOG_FILENAME = 'auto_updater.log'
BACKUP_WORLD_NAME = "Test World"

# CONFIGURATION Windows - Un-comment and set if running on Windows
#BACKUP_DIR = 'path to backup directory'
#BACKUP_WORLD = 'path to current running world'
#current_server_path = u'..\\minecraft_server.jar'
# I use a bat file to run server
#start_mc_file = u'..\\minecraft_server_start.bat'

# CONFIGURATION Linux, Darwin - Un-comment and set if running on Kinux, Darwin
#BACKUP_DIR = 'path to backup directory'
#BACKUP_WORLD = 'path to current running world'
#current_server_path = u'..\\server.jar'
# I use a bash file to run server
#start_mc_file = u'..\\minecraft_server_start.sh' 


logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filename=LOG_FILENAME,level=logging.INFO)
#logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO)

cur_ver = None

def kill_server(platform_system):
    logging.info('Stopping server.')
    platform_system = platform.system()
    if platform_system == 'Windows':
        output = os.popen('wmic process get description, processid').read()
    elif platform_system == 'Linux' or platform_system == 'Darwin':
        output = os.popen('ps -ef | grep minecraft_server').read()
        
    for process in output.split("\n"):
        if platform_system == 'Windows':
            # Find the java.exe processes and kill them    
            if "java.exe" in process:
                process_name = ' '.join(process.split()).split(" ")
                logging.info("\tFound java.exe " + process)
                #logging.info("\tFound java.exe " + process_name[0])
                os.system("taskkill /f /im " + process_name[0])
        else:
            #if 'minecraft_server_start' in process or 'java' in process:
            if 'java' in process:
                logging.info("\tFound java {}".format(process))
                process = ' '.join(process.split()).split(" ")
                print("process ", process)
                process_pid = process[1]
                print("process_pid ", process_pid)
                os.system("kill -9 " + process_pid)

def server_checksum():
    # get checksum of running server
    if os.path.exists('../minecraft_server.jar'):
        sha = hashlib.sha1()
        f = open("../minecraft_server.jar", 'rb')
        sha.update(f.read())
        cur_ver = sha.hexdigest()
    else:
        cur_ver = ""
    return cur_ver

def update_server():
    global cur_ver

    # retrieve version manifest
    response = requests.get(MANIFEST_URL)
    data = response.json()

    if UPDATE_TO_SNAPSHOT:
        minecraft_ver = data['latest']['snapshot']
    else:
        minecraft_ver = data['latest']['release']

    logging.info('Running Minecraft Updater')

    for version in data['versions']:
        if version['id'] == minecraft_ver:
            jsonlink = version['url']
            jar_data = requests.get(jsonlink).json()
            jar_sha = jar_data['downloads']['server']['sha1']

            logging.info('\tYour sha1 is ' + cur_ver + '. Latest version is ' + str(minecraft_ver) + " with sha1 of " + jar_sha)

            if cur_ver != jar_sha:
                logging.info('\tUpdating server...')
                link = jar_data['downloads']['server']['url']
                logging.info('\tDownloading .jar from ' + link + '...')
                response = requests.get(link)
                with open('minecraft_server.jar', 'wb') as jar_file:
                    jar_file.write(response.content)
                logging.info('\tDownloaded.')

                logging.info('\tUpdating server .jar')
                if os.path.exists(current_server_path):
                    os.remove(current_server_path)

                os.rename('minecraft_server.jar', current_server_path)
            else:
                logging.info('\tServer is already up to date.')

def make_backup():
    global cur_ver

    logging.info('Backing up world...')
    try:
        # Remove any backups older than 3 days
        logging.info('\tRemoving backups older than 3 days')
        now = time.time()
        dir_list = os.listdir(BACKUP_DIR)
        print("{}".format(dir_list))
        for f in dir_list:
            print("{}".format(f))
            f_path = os.path.join(BACKUP_DIR, f)

            if os.stat(f_path).st_mtime < now - 3 * 86400:
                if os.path.isdir(f_path):
                    shutil.rmtree(f_path)

        # Backup current world
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        backupPath = os.path.join(
            BACKUP_DIR,
            BACKUP_WORLD_NAME + "_backup_" + datetime.now().isoformat().replace(':', '-') + "_sha=" + cur_ver)
        shutil.copytree(BACKUP_WORLD, backupPath)
        logging.info('\tBacked up world to:\n\t{}.'.format(backupPath))
    except shutil.Error as e:
        logging.info("Error occured while making backup:\n\tError: {}".format(e))
        pass

def main():
    global cur_ver
    platform_system = platform.system()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("Stopping server")
    kill_server(platform_system)
    time.sleep(5)
    # get checksum of running server
    cur_ver = server_checksum()
    make_backup()
    update_server()

    logging.info('\tRe-Starting server...')
    time.sleep(5)
    if platform_system == 'Windows':
        #os.system(win_start_mc_file) # restart without reboot
        os.system("shutdown /r")     # restart with reboot
    else: # Linux, Darwin
        os.system(lin_start_mc_file) # restart without reboot
        
        
if __name__ == "__main__":
    main()    


'''
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# retrieve version manifest
response = requests.get(MANIFEST_URL)
data = response.json()

if UPDATE_TO_SNAPSHOT:
    minecraft_ver = data['latest']['snapshot']
else:
    minecraft_ver = data['latest']['release']

# get checksum of running server
if os.path.exists('../minecraft_server.jar'):
    sha = hashlib.sha1()
    f = open("../minecraft_server.jar", 'rb')
    sha.update(f.read())
    cur_ver = sha.hexdigest()
else:
    cur_ver = ""
logging.info('Running Minecraft Updater')

for version in data['versions']:
    if version['id'] == minecraft_ver:
        jsonlink = version['url']
        jar_data = requests.get(jsonlink).json()
        jar_sha = jar_data['downloads']['server']['sha1']

        logging.info('\tYour sha1 is ' + cur_ver + '. Latest version is ' + str(minecraft_ver) + " with sha1 of " + jar_sha)

        if cur_ver != jar_sha:
            logging.info('\tUpdating server...')
            link = jar_data['downloads']['server']['url']
            logging.info('\tDownloading .jar from ' + link + '...')
            response = requests.get(link)
            with open('minecraft_server.jar', 'wb') as jar_file:
                jar_file.write(response.content)
            logging.info('\tDownloaded.')
#            os.system('screen -S minecraft -X stuff \'say ATTENTION: Server will shutdown for 1 minutes to update in 30 seconds.^M\'')
#            logging.info('Shutting down server')

#            for i in range(20, 9, -10):
#                time.sleep(10)
#                os.system('screen -S minecraft -X stuff \'say Shutdown in ' + str(i) + ' seconds^M\'')

#            for i in range(9, 0, -1):
#                time.sleep(1)
#                os.system('screen -S minecraft -X stuff \'say Shutdown in ' + str(i) + ' seconds^M\'')
#            time.sleep(1)

            logging.info('Stopping server.')
            output = os.popen('wmic process get description, processid').read()
            for process in output.split("\n"):
            # Find the java.exe processes and kill them    
                if "java.exe" in process:
                    process_name = ' '.join(process.split()).split(" ")
                    logging.info("\tFound java.exe " + process_name[0])
                    os.system("taskkill /f /im " + process_name[0])

            logging.info('Backing up world...')

            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            
            backupPath = os.path.join(
                BACKUP_DIR,
                "world" + "_backup_" + datetime.now().isoformat().replace(':', '-') + "_sha=" + cur_ver)
            shutil.copytree(BACKUP_WORLD, backupPath)

#            logging.info('Backed up world.')
            logging.info('\tUpdating server .jar')

            if os.path.exists('../minecraft_server.jar'):
                os.remove('../minecraft_server.jar')

            os.rename('minecraft_server.jar', '../minecraft_server.jar')
#            logging.info('Starting server...')
#            os.chdir("..")
#            os.system('screen -S minecraft -d -m java -Xms16G -Xmx16G -jar minecraft_server.jar')

            logging.info('\tRe-Starting server...')
            time.sleep(5)
            os.system("shutdown /r")

        else:
            logging.info('Backing up world...')
            try:
                # Remove any backups older than 3 days
                logging.info('\tRemoving backups older than 3 days')
                now = time.time()
                dir_list = os.listdir(BACKUP_DIR)
#                print("{}".format(dir_list))
                for f in dir_list:
                    print("{}".format(f))
                    f_path = os.path.join(BACKUP_DIR, f)
#                    print("{}".format(f_path))
#                    print("Last modified: %s" % time.ctime(os.path.getmtime(f_path)))
#                    print("Created: %s" % time.ctime(os.path.getctime(f_path)))
#                    print("now {}".format(now))
#                    print("now - 3 * 86400 {}".format(now - 3 * 86400))
#                    print("file time {}".format(os.stat(f_path).st_mtime))
#                    print("os.stat(f_path).st_mtime < now - 3 * 86400 {}".format(os.stat(f_path).st_mtime < now - 0 * 86400))

                    if os.stat(f_path).st_mtime < now - 3 * 86400:
                        if os.path.isdir(f_path):
                           shutil.rmtree(f_path)

                # Backup current world
                if not os.path.exists(BACKUP_DIR):
                    os.makedirs(BACKUP_DIR)

                backupPath = os.path.join(
                    BACKUP_DIR,
                    BACKUP_WORLD_NAME + "_backup_" + datetime.now().isoformat().replace(':', '-') + "_sha=" + cur_ver)
                shutil.copytree(BACKUP_WORLD, backupPath)
            except shutil.Error as e:
                pass
            logging.info('Backed up world.')
            logging.info('\tServer is already up to date.')

        break
'''    