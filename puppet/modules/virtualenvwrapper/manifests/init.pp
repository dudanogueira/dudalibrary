class virtualenvwrapper {

  package { 'virtualenvwrapper':
    ensure   => 'latest',
    provider => 'pip',
    require  => Package['python-pip'],
  }

  file_line { 'virtualenvwrapper_script':
    path    => '/home/vagrant/.bashrc',
    line    => 'source /usr/local/bin/virtualenvwrapper.sh',
    require => Package['virtualenvwrapper'],
  }

  file_line { 'virtualenvwrapper_project_home':
    path    => '/home/vagrant/.bashrc',
    line    => 'export PROJECT_HOME=/home/vagrant/',
    require => Package['virtualenvwrapper'],
  }
}