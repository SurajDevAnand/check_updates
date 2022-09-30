#!/usr/bin/python

import sys
import json
import subprocess

PYTHON_MAJOR_VERSION = sys.version_info[0]
if PYTHON_MAJOR_VERSION == 3:
            import distro as platform
elif PYTHON_MAJOR_VERSION == 2:
            import platform 
            
os_info = platform.linux_distribution()[0].lower()
PLUGIN_VERSION = "1"
HEARTBEAT="true"

data={}
data['plugin_version'] = PLUGIN_VERSION
data['heartbeat_required']=HEARTBEAT
data['packages_to_be_updated']=0
data['security_updates']=0

command="yum check-update --security | grep -i 'needed for security'"

def get_command_output(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return output

if 'centos' in os_info or 'red hat' in os_info:
        out = get_command_output(command)
        if out:
            out = out.rstrip()
            count = out.split("needed for security")
            security_count = count[0].split()[0]
            if security_count == 'No':
                data['security_updates'] = 0
            else:
               data['security_updates'] = security_count
            packages_count = count[1].split()
            for each in packages_count:
                 if each.isdigit():
                     data['packages_to_be_updated']=each

elif 'debian' in os_info:
    command1="apt-get -q -y --ignore-hold --allow-change-held-packages --allow-unauthenticated -s dist-upgrade | /bin/grep  ^Inst | wc -l"
    command2=""
    out=get_command_output(command1)
    if out:
        data["packages_to_be_updates"]=out

                
else:    
    file_path='/var/lib/update-notifier/updates-available'
    lines = [line.strip('\n') for line in open(file_path)]
    for line in lines:
        if line:
            if ( 'packages can be updated' in line ) or ('can be installed immediately' in line ) or ('can be applied immediately' in line):
                data['packages_to_be_updated'] = line.split()[0]
            if ('updates are security updates' in line) or ('updates are standard security updates' in line):
                data['security_updates'] = line.split()[0]
                
print(json.dumps(data))
