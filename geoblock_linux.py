# This program scans all IPs connected to the machine to determine if it's coming from
# a sanctioned Country and blocks the IP in the firewall. Linux only (Works with iptables)

# Needed functions
import requests
import subprocess
import os
import time
import platform

print('This program will only work on Linux due to the code working with iptables.');
print('Checking OS system...');

# Checks OS system to ensure code won't break
if(platform.system() != 'Linux'):
    print(f"Sorry, you're on {platform.system()}. Please switch to a Linux system.");
    print('Closing in 5 seconds...');
    time.sleep(5);
    quit();

# Get host IP address
print('Getting your IP address...')
hostname = os.popen('hostname').read().strip();
host_ip = os.popen('hostname -I').read().strip();
print(f'IP address found: {host_ip}');

# Bad IPs that have been banned.
ip_banned_list = [];

def get_ip_location(ip):
    try:
        # Pulls IP data to find Country
        ip_request = requests.get(f'http://ipinfo.io/{ip}/json');
        ip_data = ip_request.json();
        country = ip_data.get('country');
        print(f"{ip} is from {country}")
        # Checks if Country is sanctioned
        check_country(ip, country);
    except Exception as e:
        return {'Error': str(e)}

def check_country(ip, country):
# Bad Country List
# Afghanistan, Albania, Belarus, Burma, Balkan, Bosnia, Central African Republic, China, Cuba, 
# Democratic Republic of Congo, Democratic People’s Republic of Korea, Ethiopia, Hong Kong, Iran, Iraq, 
# Kosovo, Lebanon, Libya, Mali, Montenegro, North Macedonia, Nicaragua, Russia, Syria, Somalia, South Sudan,
# Sudan, Serbia, Ukraine, Venezuela, Yemen
    bad_country_list = ['AF', 'BY', 'CF', 'CH', 'CN', 'CD', 'KP', 'ET', 'HK', 'IR', 'IQ', 
'LB', 'LY', 'ML', 'NI', 'RU', 'SY', 'SO', 'SS', 'SD', 'UA', 'VE', 'YE', 'AL', 
'BA', 'ME', 'XK', 'MK', 'RS'];
    # Checks if IP is from sanctioned Country

    for current_country in bad_country_list:
        if (country == current_country and ip not in ip_banned_list):
            print(f'{ip} is being added to firewall.');
            add_to_firewall(ip);

    def add_to_firewall(ip):
        # Adds the bad IP to firewall
        iptable_command = f"sudo iptables -A INPUT -s {ip} -j DROP";
        os.system(iptable_command);

        # Adds ip to ip_banned_list
        ip_banned_list.append(ip);
        print(f"{ip} was added to firewall.");

# Runs the program throughout run time
while True:
    print('Scanning for foreign IP addresses...')

    # Grabs all IPs running through a socket

    netstat_ip_grab_command = 'netstat -n | awk \'$5 \' | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}"';
    # Grabs results of above
    netstat_output = subprocess.check_output(netstat_ip_grab_command, shell=True, encoding='utf-8');

    # Makes the output readable
    netstat_var = netstat_output.strip();
    netstat_var = netstat_var.split();

# Loops through new array above
    for ip in netstat_var:
        # Stops loopback and local IP
        if ip != host_ip and ip !='127.0.0.1':
            get_ip_location(ip);
    # Waits 30 seconds before running again.
    time.sleep(30);