### Welcome

This repository holds my course materials for the *pythonengine* project.

The idead behind this project is to create a tool for automation.
The main parts are a Postgres database, an engine and a webapp for easier management.

The idea is to make this tool pluggable so that you can develop your own extensions while retaining simplicity.

This is a birds eye view of the project.

![overview](/Pics/birdseye.png)

The following dependencies are in place:
- Python3.7
- ansible
- Postgres database
- At least 3 VM-s, not necessary have to run at once

The following guides are available:
- [Create Users](./Guides/UserCreate.md)
- [Python from Source](./Guides/PythonBuild.md)
- [Install Ansible](./Guides/Ansible.md)
- [Install PostGres](./Guides/postgresinstall.md)
- [Invoke Tutorial](./Guides/InvokeTut.md)