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

## Windows

I recommend just running under WSL2

# Windows running WSL2

Install and run Docker Desktop. 

Install an ssh server if not yet installed andd set it to port 2022

Inside the WSL2 instance run:

```
sudo apt install openssh-server
sudo sed -i -E 's,^#?Port.*$,Port 2022,' /etc/ssh/sshd_config
sudo sh -c "echo '${USER} ALL=(root) NOPASSWD: /usr/sbin/service ssh start' >/etc/sudoers.d/service-ssh-start"
sudo service ssh restart
```
Once the service is restarted, make sure it is on port 2022:
```
$ sudo /usr/sbin/service ssh status
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled; vendor preset: enabled)
     Active: active (running) since Thu 2024-08-22 15:23:15 PDT; 1s ago
       Docs: man:sshd(8)
             man:sshd_config(5)
    Process: 350379 ExecStartPre=/usr/sbin/sshd -t (code=exited, status=0/SUCCESS)
   Main PID: 350380 (sshd)
      Tasks: 1 (limit: 37996)
     Memory: 1.8M
     CGroup: /system.slice/ssh.service
             └─350380 "sshd: /usr/sbin/sshd -D [listener] 0 of 10-100 startups"

Aug 22 15:23:15 Chris-Main-PC systemd[1]: Starting OpenBSD Secure Shell server...
Aug 22 15:23:15 Chris-Main-PC sshd[350380]: Server listening on 0.0.0.0 port 2022.
Aug 22 15:23:15 Chris-Main-PC sshd[350380]: Server listening on :: port 2022.
Aug 22 15:23:15 Chris-Main-PC systemd[1]: Started OpenBSD Secure Shell server.
```
Also make sure that you can write to the authorized keys
```
chmod 600 ~/.ssh/authorized_keys
```

From WSL2, you should now add the key:
```
$ ssh-copy-id -p 2022 cdk2128@localhost
/usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/cdk2128/.ssh/id_rsa-remote-ssh.pub"
The authenticity of host '[localhost]:2022 ([127.0.0.1]:2022)' can't be established.
ED25519 key fingerprint is SHA256:fjByvCvFZiL3IfOAnRDHeZFn7yylWjFNJwfY2cEnaQo.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
/usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
/usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys

Number of key(s) added: 1

Now try logging into the machine, with:   "ssh -p '2022' 'cdk2128@localhost'"
and check to make sure that only the key(s) you wanted were added.
```

If you want you can also add it from Powershell:
```
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh cdk2128@localhost -p 2022 "cat >> .ssh/authorized_keys"
```


## Debian/Ubuntu/WSL2

If Python3 and Pip3 are not installed run:
```
sudo apt install python3
sudo apt install python3-pip
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

You can also use this file to overwrite variables for the specific installation without overwriting the github project code. For example, you may have the following to specify the user and location of the configuration files:

```
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

dx_docker_registry: "registry.cklein.us"
docker_user: cdk2128
docker_config_dir: /usr/src/docker/elk
```

Next, Ansible needs to be able to connect to the localhost using ssh and act as a super user. This is easiest if you have a private certificate file. Use ssh-copy-id to easily achieve that if you have not done so yet.

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

Now all we have to do is add the user to not request a password when sudoing to root:
```
echo "%${USER} ALL=(ALL) NOPASSWD:ALL" | sudo EDITOR='tee ' visudo --quiet --file=/etc/sudoers.d/passwordless-sudo
```

Now, you should be able to connect to the local host and sudo up without passwords:
```
$ ssh christian.klein@localhost
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
