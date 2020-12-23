from invoke import task
import os

@task
def localCommand(c):
        os.system('df -h')

@task
def localUpTime(c):
        os.system('uptime')

@task
def remoteDiskUsage(c, Machine = None):
        if Machine:
                os.system(f"ansible-playbook remote.yaml -e FQDN={Machine} ")
        else:
                print("Machine is a mandatory argument!")

@task
def localWithArgs(c,User = None):
        if User:
                os.system(f"ps aux | grep {User}")
        else:
                print("Please specify the user for this!")