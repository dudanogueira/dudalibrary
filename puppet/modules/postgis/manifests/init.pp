# Installs and starts postgis
class postgis {
  include apt
  apt::ppa { 'ppa:ubuntugis':}
  package {'postgresql':
    ensure => present,
    require  => Exec['apt-get update'];
  }
  package {'postgresql-9.1-postgis':
    ensure  => present,
    require => [Apt::Ppa['ppa:ubuntugis'],
    Package['postgresql']],
  }
  # setup the postgis_template
  exec { 'create_template_db':
    command => '/usr/bin/createdb template_postgis',
    cwd     => '/var/lib/postgresql',
    group   => 'postgres',
    user    => 'postgres',
    require => [Service['postgresql'],Package['postgresql-9.1-postgis']],
    returns => [0,1],
    #unless  => 'sudo -u postgres psql -l | grep template_postgis | wc -l'
    unless  => '/usr/bin/psql -l | /usr/bin/grep template_postgis | /usr/bin/wc -l'
  }
  
  exec { 'create_template_sql':
    command => '/usr/bin/psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-2.0/postgis.sql',
    cwd     => '/var/lib/postgresql',
    group   => 'postgres',
    user    => 'postgres',
    require => Exec['create_template_db'],
    returns => [0,1],
    unless  => '/usr/bin/psql -l | /usr/bin/grep template_postgis | /usr/bin/wc -l'
  }
  
  exec { 'create_template_sys_sql':
    command => '/usr/bin/psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-2.0/spatial_ref_sys.sql',
    cwd     => '/var/lib/postgresql',
    group   => 'postgres',
    user    => 'postgres',
    require => Exec['create_template_sql'],
    returns => [0,1],
    unless  => '/usr/bin/psql -l | /usr/bin/grep template_postgis | /usr/bin/wc -l'
  }
}
