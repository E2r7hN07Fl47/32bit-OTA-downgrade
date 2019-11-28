import paramiko
import argparse
import shutil
import os


parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="localhost", help="Input SSH IP. By default, localhost.")
parser.add_argument("--port", type=int, default=22, help="Input SSH port. By default, 22")
parser.add_argument("--login", "-l", default="root", help="Input SSH login. By default, root")
parser.add_argument("--password", "-p", default="alpine", help="Input SSH password. By default, alpine")
parser.add_argument("--new", "-n", action="store_true", help="Allows to downgrade to 8.4.1. By default, False")
parser.add_argument("--restore", "-r", action="store_true", help="Restores SystemVersion.plist from backup. By default, False")
parser.add_argument("--update", "-u", action="store_true", help="Allows to install 9.3.6. By default, False")
parser.add_argument("--no-backup", "-nb", action="store_true", help="Tool will not make backups. By default, False")
parser.add_argument("--custom", "-c", action="store_true", help="Allows to configure custom info. By default, False")
parser.add_argument("--version", "-v", default=None, help="Input custom version if --custom uses. By default, None")
parser.add_argument("--build", "-b", default=None, help="Input custom build if --custom uses. In default, None")

args = parser.parse_args()

ip = args.ip
port = args.port
login = args.login
password = args.password
restore = args.restore
no_backup = args.no_backup
install_new = args.new
install_latest = args.update
install_custom = args.custom
custom_version = args.version
custom_build = args.build

if (install_new and (install_latest or install_custom)) or (install_latest and install_custom):
    print("Conflict arguments")
    raise argparse.ArgumentError

sshClient = paramiko.SSHClient()
sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sshClient.connect(hostname=ip, port=port, username=login, password=password)

open("SystemVersion.plist", "w")

sftpClient = sshClient.open_sftp()

if restore:
    if os.path.exists("SystemVersion.plist.bak"): 
        sftpClient.put("SystemVersion.plist.bak", "/System/Library/CoreServices/SystemVersion.plist")
        print("Successfully restored file from backup")
    else:
        print("Oops, there is no backup")
else:
    sftpClient.get("/System/Library/CoreServices/SystemVersion.plist", "SystemVersion.plist")

    if not os.path.exists("SystemVersion.plist.bak") and not no_backup:
        shutil.copy2("SystemVersion.plist", "SystemVersion.plist.bak")

    with open("SystemVersion.plist") as file:
        lines = file.readlines()
        if install_new:
            lines[5] = "    <string>10B329</string>\n"
            lines[11] = "    <string>6.1.3</string>\n"
        elif install_latest:
            lines[5] = "    <string>11D167</string>\n"
            lines[11] = "    <string>7.1</string>\n"
        elif install_custom:
            lines[5] = f"    <string>{custom_build}</string>\n"
            lines[11] = f"    <string>{custom_version}</string>\n"
        else:    
            lines[5] = "    <string>9A334</string>\n"
            lines[11] = "    <string>5.0</string>\n"
    with open("SystemVersion.plist", 'w') as file:
        file.writelines(lines)
    
    sftpClient.put("SystemVersion.plist", "/System/Library/CoreServices/SystemVersion.plist")
    if install_new or install_latest or not install_custom:
        ver = "8.4.1" if install_new else "9.3.6" if install_latest else "6.1.3"
        mod = "6.1.3" if install_new else "7.1" if install_latest else "5.0"
        print(f"Successfully modified to {mod}, go to OTA updates and download iOS {ver}")
    else:
        print(f"Successfully modified to {custom_version}")
    
sftpClient.close()
    
sshClient.close()