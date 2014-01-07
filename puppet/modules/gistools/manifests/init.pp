# Installs gis tools from ubuntugis
class gistools {

  $gis_packages = ['gdal-bin','libgdal1-dev']

  package { $gis_packages :
    ensure  => present,
    require => Apt::Ppa['ppa:ubuntugis'],
  }
  #proj geos gdal ogr postgis cairo wmsclient wfs wfsclient wcs curl-config xml2-config sos fastcgi freetype gd jpeg png kml threads libsvg-cairo php
  #proj geos, gdal, ogr, postgis
}
