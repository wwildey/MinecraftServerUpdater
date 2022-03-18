# MinecraftServerUpdater

This script is a modification of the script found at https://github.com/eclair4151/MinecraftUpdater 
and has been modified to run on both Windows and Linux platforms. 

This is a python package to automate the updating of your server. Its so annoying to try and download the jar, ftp it over, stop the server, back up your world, etc. This automates alll that. just git clone this in the root of your server so there is an extra folder. Then run python update.py in the new folder. it will check if you have the latest version. If not if will download the latest jar, then using screen it will announce to the server that it will shutdown and give a 30 seconds countdown before stopping the server. it will then backup your world into a new folder when it updates incase something goes wrong. then update the server jar and start the server back up in screen so its in the background.

Configuration
Latest vs. Snapshot
UPDATE_TO_SNAPSHOT = <True,False>

Backup Directory
BACKUP_DIR =

Log File
LOG_FILENAME =

# Examples:
# Common config settings 
UPDATE_TO_SNAPSHOT = False
MANIFEST_URL = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
LOG_FILENAME = 'auto_updater.log'
BACKUP_WORLD_NAME = '<minecraft World name>'

# CONFIGURATION Windows - Un-comment and set if running on Windows
# BACKUP_DIR = '<path to backup directory>'
# BACKUP_WORLD = '<path to current running world>'
# current_server_path = u'..\\minecraft_server.jar'
# I use a bat file to run server
# start_mc_file = u'..\\minecraft_server_start.bat'

# CONFIGURATION Linux, Darwin - Un-comment and set if running on Kinux, Darwin
# BACKUP_DIR = '<path to backup directory>'
# BACKUP_WORLD = '<path to current running world>'
# current_server_path = u'..\\server.jar'
# I use a bash file to run server
# start_mc_file = u'..\\minecraft_server_start.sh' 


Scheduling Updates
This script is intended to be run as a cron job on Linux.
This script is intended to be run as a task on Windows.

NOTE: This has not been tested on Darwin(Mac) platforms but should work.

NOTE: Current settings assume that this script is placed in a sub-directory of the server,jar location
