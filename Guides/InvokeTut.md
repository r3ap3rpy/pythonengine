### Invoke tutorial

This guide shows you how to get used to creating small cli apps.

First the module has to be installed.

``` bash
python3 -m pip install invoke
```

Then create the following file called *tasks.py* under your preferred location.

``` python
from invoke import task

@task
def helloWorld(c, A = None, B = None):
        c.run(f""" echo "{A}" > /tmp/{B}  """)

@task
def remoteCommand(c, Machine = None, Command = None):
        if Machine and Command:
                c.run(f"ansible -m command -a '{Command}' {Machine}")
        else:
                print("Machine and Command are mandatory")
```

After saving it you will see that when you issue the *invoke --list* it gives you the following output.

``` bash
Available tasks:

  helloWorld
  remoteCommand
```

If you invoke the *helloWorld* this is what follows for example *invoke helloWorld -A whaaksjd -B aksjdkasjd*

``` bash
[pyengine@centos invokedemo]$ cat /tmp/aksjdkasjd
whaaksjd
```

If you invoke the *remoteCommand* this is what follows for example *invoke remoteCommand --Machine ubuntu --Command "uptime"*

``` bash
[pyengine@centos invokedemo]$ invoke remoteCommand --Machine ubuntu --Command "uptime"
ubuntu | CHANGED | rc=0 >>
 18:18:45 up  1:22,  3 users,  load average: 0,00, 0,02, 0,00
```