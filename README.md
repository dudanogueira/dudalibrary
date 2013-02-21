dudalibrary
===========


Open Source OER (Open Educational Resource) Manager (beta)

This software is still in beta. If you find any problems, let us know!

Installation for test/dev
===========
 * Copy the dudalibrary/settings.py.dist to dudalibrary/settings.py
 * Install the requirements: See below
 * Synchronize the database by running: python manage.py syncdb
 * Migrate the datavase by running: python manage.py syncdb
 * Run the test/dev server by running: python manage.py runserver
 * Access Duda Library at: http://127.0.0.1:8000

Installation for production
===========

For a production use case, you certainly will want to:
 * Make use of a real web server under it (eg: Apache, etc)
 * Make use of MySql or PostgreSQL databases.
 * Make sure you can read/write all path listed on settings.py (future check command to come!)
 * Make sure to change the secret from settings.py to a private one ;)

Dependencies
===========

Check out the dependencies at pip_requirements.txt (you can try: pip install -r requirements.txt)
Also, need to install xapian inside your virtualenv. (see below)


Xapian Core and Bindings Installation on VirtualEnv
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