### Python Build 

This guide shows you how to build python 3.7.0 from source.

The follwing steps are need to be done in *bash*, if you use a system where you have at least Python3.7.0 you can skip this.

``` bash
sudo su -
cd /tmp
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
wget https://www.openssl.org/source/old/1.0.2/openssl-1.0.2.tar.gz
tar xvfz Python-3.7.0.tgz
tar xvfz openssl-1.0.2.tar.gz
echo "export LD_LIBRARY_PATH=/usr/local/ssl/lib/" >> "/root/.bashrc"
echo "export LD_LIBRARY_PATH=/usr/local/ssl/lib/" >> "/home/pyengine/.bash_profile"
cd /tmp/openssl-1.0.2
./config shared
make install
cd ..
cd /tmp/Python-3.7.0
./configure --enable-loadable-sqlite-extensions --enable-optimizations --without-ensurepip --with-openssl=/usr/local/ssl
make altinstall
update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 1
echo "1"|update-alternatives --config python3
which pip && `echo "y" | pip uninstall pip`
/usr/local/bin/python3.7 /tmp/get-pip.py
update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.7 1
echo "1"|update-alternatives --config pip
```
