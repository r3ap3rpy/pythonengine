### Python Build 

This guide shows you how to build python 3.7.0 from source.

The follwing steps are need to be done in *bash*, if you use a system where you have at least Python3.7.0 you can skip this.

``` bash
sudo su -
yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel sqlite-devel -y
cd /tmp
wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
wget https://www.openssl.org/source/old/1.0.2/openssl-1.0.2.tar.gz
wget https://bootstrap.pypa.io/get-pip.py
tar xvfz Python-3.7.0.tgz
tar xvfz openssl-1.0.2.tar.gz
echo "export LD_LIBRARY_PATH=/usr/local/ssl/lib/" >> "/root/.bashrc"
echo "export LD_LIBRARY_PATH=/usr/local/ssl/lib/" >> "/home/pyengine/.bash_profile"
cd /tmp/openssl-1.0.2
/config --prefix=/usr/local/openssl --openssldir=/usr/local/openssl shared zlib
make
make install
vi /etc/profile.d/openssl.sh
# /etc/profile.d/openssl.sh
pathmunge /usr/local/openssl/bin
vi /etc/ld.so.conf.d/openssl-1.0.2.conf
# /etc/ld.so/conf.d/openssl-1.0.2.conf
/usr/local/openssl/lib
ldconfig -v
cd ..
cd /tmp/Python-3.7.0
./configure --enable-loadable-sqlite-extensions --enable-optimizations --without-ensurepip --with-openssl=/usr/local/ssl
make altinstall
update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 1
echo "1"|update-alternatives --config python3
which pip && `echo "y" | pip uninstall pip`
/usr/local/bin/python3.7 /tmp/get-pip.py
update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3.7 1
echo "1"|update-alternatives --config pip
```
