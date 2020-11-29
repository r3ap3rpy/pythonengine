### Ansible Setup

This guide shows you how to setup ansible on your worker nodes hosting the python engine.

In bash execute the following commands.

``` bash
yum install epel-release -y
yum install python3-devel ansible -y

echo "---" >> /etc/ansible/group_vars/WIN.yaml
echo "ansible_user: pyengine" >> /etc/ansible/group_vars/WIN.yaml
echo "ansible_password: pyengine!123" >> /etc/ansible/group_vars/WIN.yaml
echo "ansible_connection: winrm" >> /etc/ansible/group_vars/WIN.yaml
echo "ansible_winrm_transport: basic" >> /etc/ansible/group_vars/WIN.yaml
echo "ansible_port: 5985" >> /etc/ansible/group_vars/WIN.yaml

