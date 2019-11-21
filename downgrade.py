import paramiko
import argparse
import shutil
import os


parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="localhost", help="Input SSH IP. In default, localhost.")
parser.add_argument("--port", type=int, default=22, help="Input SSH port. In default, 22")
parser.add_argument("--login", "-l", default="root", help="Input SSH login. In default, root")
parser.add_argument("--password", "-p", default="alpine", help="Input SSH password. In default, alpine")
parser.add_argument("--new", "-n", action="store_true", help="Allows to downgrade to 8.4.1. In default, False")
parser.add_argument("--restore", "-r", action="store_true", help="Restores SystemVersion.plist from backup. In default, False")
parser.add_argument("--update", "-u", action="store_true", help="Allows to install 9.3.6. In default, False")
parser.add_argument("--no-backup", "-nb", action="store_true", help="Tool will not make backups. In default, False")

args = parser.parse_args()

ip = args.ip
port = args.port
login = args.login
password = args.password
restore = args.restore
no_backup = args.no_backup
install_new = args.new
install_latest = args.update


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
        else:    
            lines[5] = "    <string>9A334</string>\n"
            lines[11] = "    <string>5.0</string>\n"
    with open("SystemVersion.plist", 'w') as file:
        file.writelines(lines)
    
    sftpClient.put("SystemVersion.plist", "/System/Library/CoreServices/SystemVersion.plist")
    ver = "8.4.1" if install_new else "9.3.6" if install_latest else "6.1.3"
    print(f"Successfully modified, go to OTA updates and download iOS {ver}")
    
sftpClient.close()
    
sshClient.close()