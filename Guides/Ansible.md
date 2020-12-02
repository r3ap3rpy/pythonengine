### Ansible Setup

This guide shows you how to setup ansible on your worker nodes hosting the python engine.

In bash execute the following commands on the centos machine!

``` bash
yum install epel-release -y
yum install python3-devel ansible -y
python3 -m pip install pywinrm
```

In bash execute the following commands on the ubuntu machine!

``` bash
apt install software-properties-common
apt-add-reposiotry --yes --update ppa:ansible/ansible
apt-get install apt-add-repository
apt-add-repository --yes --update ppa:ansible/ansible
apt-get install ansible -y
apt-get install python3-pip -y
python3 -m pip install pywinrm
```

On both machine perform the following commands.

``` bash
chown -R pyengine.pyengine /etc/ansible
echo "" > /etc/ansible/hosts
mkdir /etc/ansible/group_vars
echo "---" >> /etc/ansible/group_vars/win.yaml
echo "ansible_user: pyengine" >> /etc/ansible/group_vars/win.yaml
echo "ansible_password: pyengine!123" >> /etc/ansible/group_vars/win.yaml
echo "ansible_connection: winrm" >> /etc/ansible/group_vars/win.yaml
echo "ansible_winrm_transport: basic" >> /etc/ansible/group_vars/win.yaml
echo "ansible_port: 5985" >> /etc/ansible/group_vars/win.yaml
```

On the windows machine execute these form administrator privileged powershell.

``` powershell
set-executionpolicy -executionpolicy remotesigned
winrm quickconfig -q
winrm set winrm/config/winrs '@{MaxMemoryPerShellMB="512"}'
winrm set winrm/config '@{MaxTimeoutms="1800000"}'
winrm set winrm/config/service '@{AllowUnencrypted="true"}'
winrm set winrm/config/service/auth '@{Basic="true"}'
```

Now you must be able to use the following commands on any of your machines!

``` bash
ansible -m ping ubuntu
ansible -m ping centos
ansible -m win_ping 2019A
```

