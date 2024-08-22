# dx-elk-sample
HCL DX and ELK log analysis setup using Ansible

# Installation
Install Python3 and pip3 if you do not have it already installed

```
$ python3 --version
Python 3.9.6
$ pip3 --version
pip 21.2.4 from /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/site-packages/pip (python 3.9)
```

Install Ansible:

```
$ pip3 install --user ansible
$ ansible --version
ansible [core 2.17.3]
  config file = /Users/christian.klein/git/dx-elk-sample/ansible.cfg
  configured module search path = ['/Users/christian.klein/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /Users/christian.klein/Library/Python/3.12/lib/python/site-packages/ansible
  ansible collection location = /Users/christian.klein/.ansible/collections:/usr/share/ansible/collections
  executable location = /Users/christian.klein/Library/Python/3.12/bin/ansible
  python version = 3.12.5 (v3.12.5:ff3bc82f7c9, Aug  7 2024, 05:32:06) [Clang 13.0.0 (clang-1300.0.29.30)] (/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12)
  jinja version = 3.1.4
  libyaml = True
```

# Prep ansible
Create a file somewhere to hold your passwords and encrypt it. By default this is set to `../.ansible_pwd` but can be adjusted in [elk.yml](./elk.yml) 

For example, from the project folder:

```
$ cat ../.ansible_pwd 
elk_passwords:
  elastic:
    user: "elastic"
    password: "Tes2024la"
  kibana:
    user: "elastic"
    password: "Tes2024la"
dx_credentials:
  user: "wpsadmin"
  password: "wpsadmin"
```

If using a private registry for DX, add the credentials to `../.ansible_pwd`:
```
$ cat ../.ansible_pwd 
elk_passwords:
  elastic:
    user: "elastic"
    password: "Tes2024la"
  kibana:
    user: "elastic"
    password: "Tes2024la"
dx_credentials:
  user: "wpsadmin"
  password: "wpsadmin"
dx_registry_credentials:
  user: "myuser"
  password: "mypassword"
```


Next, Ansible needs to be able to connect to the localhost using ssh and act as a super user. This is easiest if you have a private certificate file. Use ssh-copy-id to easily achieve that.

Example:
```
ssh-copy-id christian.klein@localhost
```

You should be able to ssh into the local system without it asking for a password now.

```
$ ssh christian.klein@localhost
Last login: Tue Aug 20 15:53:32 2024 from ::1
$ 
```

Now all we have to do is add the user to not request a password when sudoing to root. Use `sudo visudo` and add the following entry below the `root ALL = (ALL) ALL` entry. Replace with your local user name:
```
...
# root and users in group wheel can run anything on any machine as any user
root            ALL = (ALL) ALL
%admin          ALL = (ALL) ALL
christian.klein  ALL=(ALL:ALL) NOPASSWD: ALL
...
```

Now, you should be able to connect to the local host and sudo up without passwords:
```
$ christian.klein@localhost
Last login: Tue Aug 20 15:54:27 2024 from ::1

$ sudo -i
# 
```

# Run the ansible playbook

## localhost dev containers
```
ansible-playbook elk.yml --extra-vars "ehosts=local" 
```

# Clean environment

Run the elk-cleanup playbook:

```
ansible-playbook elk-clean.yml --extra-vars "ehosts=local"
```





# THE FOLLOWING HAS TO BE REVIEWED AND CLEANED UP
TODO: Clean up and review ansible tags and docker profiles
TODO: Document start / cleanup script

# Docker profiles and services

| Profile | Service         |
|---------|-----------------|
|all      |elk_setup        |
|         |es01             |
|         |kibana           |
|         |logstash         |
|         |dx_setup         |
|         |dx               |
|         |dxlogviewer      |
|         |dx_filebeat_setup|
|         |dxfilebeat       |
|elk      |elk_setup        |
|         |es01             |
|         |kibana           |
|         |logstash         |
|         dx|dx_setup       |
|         |dx               |
|         |dxlogviewer      |
|         |dx_filebeat_setup|
|         |dxfilebeat       |
|debug    |dxdebug          |

# Start the environment

Still a bit convoluted since docker compose up is having issues from ansible

- Run the ansible prep ansible tag:
  ```
  ansible-playbook -i inventory elk.yml --tags "prep"
  ```
  This copies all files to the target docker host.

- On the docker host, start the elk profile and wait until all the elk services are up.
  ```
  docker compose --profile elk up -d
  ```
  You can monitor the progress using:
  ```
  docker compose --profile elk logs -f
  ```
  You can monitor the progress using:

- Once all services are up, start the dx profile
  ```
  docker compose --profile dx up -d
  ```

- Run the ansible postconfig ansible tag:
  ```
  ansible-playbook -i inventory elk.yml --tags "postconfig"
  ```
- Restart the dx dxlogviewer container
  ```
  docker compose --profile all restart dxlogviewer
  ```
