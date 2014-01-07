# BASE CONFS
$tz = 'America/Sao_Paulo' # Timezone
$project = 'dudalibrary' # Used in nginx and uwsgi
$domain_name = 'dudalibrary.org'
$username = 'dudalibrary' # User to create
$db_password = 'dudalibrary' # Mysql password for $db_user
$db_name = 'dudalibrary' # Mysql database name to create

# basic bootstrap
exec { 'apt-get update':
  command => '/usr/bin/apt-get update'
}

package {
  'python-dev': ensure   => 'installed',
  require  => Exec['apt-get update'];
}

package {
  'python-pip': ensure   => 'latest',
  require  => [Package['python-dev'], Exec['apt-get update']];
}

$packages = [ 'build-essential', 'python-software-properties', 'ffmpeg', 'ffmpegthumbnailer', 'g++', 'libjpeg' 'libjpeg-dev' 'libfreetype6' 'libfreetype6-dev' 'zlib1g-dev']
package {
  $::packages :
    ensure  =>  'installed',
    require => [ Package['python-dev'], Exec['apt-get update'] ],
}

# ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/
# ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/
# ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/

class { 'elasticsearch':
   java_install => true,
   package_url => 'https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.9.deb'
}

# modules installation
include postgis
include gistools

#$packages_python = [ 'django', 'psycopg2', 'South', 'django-admin-bootstrapped', 'six', 'django-extensions', 'django-haystack', 'django-tagging', 'docutils', 'python-dateutil', 'pillow', 'pyelasticsearch', 'werkzeug', 'BeautifulSoup']

$packages_python = [ 'django', 'psycopg2']

package {
  $::packages_python :
    ensure => 'installed',
    provider => pip,
    require => Package['postgresql','postgresql-9.1-postgis', 'python-dev', 'python-pip'];
}

#include postgresql::server
#postgresql::server::db{ 'dudalibrary':
#  user          => 'dudalibrary',
#  password      => 'dudalibrary',
#  grant         => 'all',
#}

#$ POSTGIS_SQL_PATH=/usr/share/postgresql/9.1/contrib/postgis-2.0
# Creating the template spatial database.
#$ createdb -E UTF8 template_postgis
##$ createlang -d template_postgis plpgsql # Adding PLPGSQL language support. not necessary
# Allows non-superusers the ability to create from this template
#$ psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
# Loading the PostGIS SQL routines
#$ psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
#$ psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
# Enabling users to alter spatial tables.
#$ psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
#$ psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
#$ psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
# SETUP FOR DUDALIBRARY DEFAULT
# CREATE USER dudalibrary_user PASSWORD 'dudalibrary_pwd';
# CREATE DATABASE dudalibrary_db OWNER dudalibrary_user TEMPLATE template_postgis ENCODING 'utf8';
