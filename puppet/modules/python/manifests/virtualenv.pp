# == Define: python::virtualenv
#
# Creates Python virtualenv.
#
# === Parameters
#
# [*ensure*]
#  present|absent. Default: present
#
# [*version*]
#  Python version to use. Default: system default
#
# [*requirements*]
#  Path to pip requirements.txt file. Default: none
#
# [*systempkgs*]
#  Copy system site-packages into virtualenv. Default: don't
#  If virtualenv version < 1.7 this flag has no effect since
#  the system packages were not supported
#
# [*distribute*]
#  Include distribute in the virtualenv. Default: true
#
# [*index*]
#  Base URL of Python package index. Default: none (http://pypi.python.org/simple/)
#
# [*owner*]
#  The owner of the virtualenv being manipulated. Default: root
#
# [*group*]
#  The group relating to the virtualenv being manipulated. Default: root
#
# [*proxy*]
#  Proxy server to use for outbound connections. Default: none
#
# [*environment*]
#  Additional environment variables required to install the packages. Default: none
#
# [*path*]
#  Specifies the PATH variable. Default: [ '/bin', '/usr/bin', '/usr/sbin' ]
#
# [*cwd*]
#  The directory from which to run the "pip install" command. Default: undef
#
# [*timeout*]
#  The maximum time in seconds the "pip install" command should take. Default: 1800
#
# === Examples
#
# python::virtualenv { '/var/www/project1':
#   ensure       => present,
#   version      => 'system',
#   requirements => '/var/www/project1/requirements.txt',
#   proxy        => 'http://proxy.domain.com:3128',
#   systempkgs   => true,
#   index        => 'http://www.example.com/simple/'
# }
#
# === Authors
#
# Sergey Stankevich
# Ashley Penney
# Marc Fournier
# Fotis Gimian
#
define python::virtualenv (
  $ensure       = present,
  $version      = 'system',
  $requirements = false,
  $systempkgs   = false,
  $distribute   = true,
  $index        = false,
  $owner        = 'root',
  $group        = 'root',
  $proxy        = false,
  $environment  = [],
  $path         = [ '/bin', '/usr/bin', '/usr/sbin','/usr/local/bin' ],
  $cwd          = undef,
  $timeout      = 1800
) {

  $venv_dir = $name

  if $ensure == 'present' {

    $python = $version ? {
      'system' => 'python',
      default  => "python${version}",
    }

    $proxy_flag = $proxy ? {
      false    => '',
      default  => "--proxy=${proxy}",
    }

    $proxy_command = $proxy ? {
      false   => '',
      default => "&& export http_proxy=${proxy}",
    }

    # Virtualenv versions prior to 1.7 do not support the 
    # --system-site-packages flag, default off for prior versions
    # Prior to version 1.7 the default was equal to --system-site-packages
    # and the flag --no-site-packages had to be passed to do the opposite
    if (( versioncmp($::virtualenv_version,'1.7') > 0 ) and ( $systempkgs == true )) {
      $system_pkgs_flag = '--system-site-packages'
    } elsif (( versioncmp($::virtualenv_version,'1.7') < 0 ) and ( $systempkgs == false )) {
      $system_pkgs_flag = '--no-site-packages'
    } else {
      $system_pkgs_flag = ''
    }

    $distribute_pkg = $distribute ? {
      true     => 'distribute',
      default  => '',
    }
    $pypi_index = $index ? {
        false   => '',
        default => "-i ${index}",
    }

    exec { "python_virtualenv_${venv_dir}":
      command => "mkdir -p ${venv_dir} ${proxy_command} && virtualenv ${system_pkgs_flag} -p ${python} ${venv_dir} && ${venv_dir}/bin/pip --log ${venv_dir}/pip.log install ${pypi_index} ${proxy_flag} --upgrade pip ${distribute_pkg}",
      user    => $owner,
      path    => $path,
      cwd     => "/tmp",
      environment => $environment,
      unless => "grep '^[ \t]*VIRTUAL_ENV=[\'\"]*/tmp[\"\']*[ \t]*$' /tmp/bin/activate", #Unless activate exists and VIRTUAL_ENV is correct we re-create the virtualenv
    }

    if $requirements {
      exec { "python_requirements_initial_install_${requirements}_${venv_dir}":
        command     => "${venv_dir}/bin/pip --log ${venv_dir}/pip.log install ${pypi_index} ${proxy_flag} -r ${requirements}",
        refreshonly => true,
        timeout     => $timeout,
        user        => $owner,
        subscribe   => Exec["python_virtualenv_${venv_dir}"],
        environment => $environment,
        cwd         => $cwd
      }

      python::requirements { "${requirements}_${venv_dir}":
        requirements => $requirements,
        virtualenv   => $venv_dir,
        proxy        => $proxy,
        owner        => $owner,
        group        => $group,
        require      => Exec["python_virtualenv_${venv_dir}"],
      }
    }
  } elsif $ensure == 'absent' {

    file { $venv_dir:
      ensure  => absent,
      force   => true,
      recurse => true,
      purge   => true,
    }
  }
}
