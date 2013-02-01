dudalibrary
===========

Open Source OER (Open Educational Resource) Manager


Dependencies
===========

Check out the dependencies at pip_requirements.txt (you can try: pip install -r requirements.txt)

Also need to install xapian inside your virtualenv.


Xapian Core and Bindings
===========

apt-get install zlib1g-dev
apt-get install g++
 
export VENV=$VIRTUAL_ENV
mkdir $VENV/packages && cd $VENV/packages
 
curl -O http://oligarchy.co.uk/xapian/1.0.16/xapian-core-1.0.16.tar.gz
curl -O http://oligarchy.co.uk/xapian/1.0.16/xapian-bindings-1.0.16.tar.gz
 
tar xzvf xapian-core-1.0.16.tar.gz
tar xzvf xapian-bindings-1.0.16.tar.gz
 
cd $VENV/packages/xapian-core-1.0.16
./configure --prefix=$VENV && make && make install
 
export LD_LIBRARY_PATH=$VENV/lib
 
cd $VENV/packages/xapian-bindings-1.0.16
./configure --prefix=$VENV --with-python && make && make install
 
python -c "import xapian" 