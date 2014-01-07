class git::clone ($repo, $username='dudalibrary') {
    $group = $username
    group { $username:
        ensure  => present,
        gid     => 2000,
    }

    user { $username:
        ensure  => present,
        gid     => $group,
        require => Group[$group],
        uid     => 2000,
        home    => "/home/${username}",
        shell   => "/bin/bash",
        managehome  => true,
    }

    file { '/opt/code' :
        ensure  => directory,
        group   => $group,
        owner   => $username,
        mode    => 0755,
    }

    file { '/home/${username}':
        ensure  => directory,
        group   => $group,
        owner   => $username,
        mode    => 0700,
    }

    package { 'git':
        ensure => installed,
    }
    
    vcsrepo { "/opt/code/${repo}":
        ensure   => latest,
        owner    => $owner,
        group    => $owner,
        provider => git,
        require  => [ Package["git"] ],
        source   => "https://github.com/dudanogueira/dudalibrary.git",
        revision => 'master',
    }
}