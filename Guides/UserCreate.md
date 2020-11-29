### User creation

Welcome, in this guide you will learn how to create users for our python engines.

Username: pyengine
Password: pyengine!123

On CentOS linux systems when you enter a root shell you should be able to add user with the following commands.

``` bash
useradd pyengine
passwd pyengine 
usermod -a -G pyengine wheel
```

On Ubuntu linux systems when you enter a root shell you should be able to add user with the following commands.

``` bash
useradd pyengine
passwd pyengine 
visudo
```

Make sure you add the passwordless sudo option in both cases.

``` bash
pyengine        ALL=(ALL)       NOPASSWD: ALL
```

On linux systems you will use either the *invoke* module of python or the *ansible* to execute automation!

On windows systems you use the same credentials and make sure the user is the member of the *Administratos* group. For windows only *ansible* will be used for authentication with *basic* auth.