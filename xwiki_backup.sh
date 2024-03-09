#!/bin/bash

#Space Separated List of Databases to Dump
#DATABASE="xwiki d1 d3"
DATABASE="xwiki"
DBUSER=root
#DBPASS=*****

# Ask for DB password
read -p "Enter DB password: " DBPASS

#XWIKI data folder
DATAFOLDER=/var/lib/xwiki/data
#Where is the webapps folder for your tomcat installation
# SLES 11 is located /srv/tomcat6/webapps
WEBAPPDIR=/usr/lib/xwiki/
#What context (dir) does your application deploy to
#DEPLOYCONTEXT=ROOT


###~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#DEPLOYDIR=${WEBAPPDIR}/${DEPLOYCONTEXT}
DEPLOYDIR=${WEBAPPDIR}

DATE=$(date '+%Y-%m-%d')
mkdir ./${DATE}

#backup mysql
echo "Backing up Mysql"
mysqldump -h 127.0.0.1 -u ${DBUSER} --password=${DBPASS} --max_allowed_packet=512m --add-drop-database --databases ${DATABASE} | /bin/gzip  > ./${DATE}/${DATABASE}.sql.gz

echo "Backing up Data"
#Backup Exteral Data Storage
/bin/tar -C ${DATAFOLDER}/../ -zcf ./${DATE}/data.tar.gz data

#Backing Java Keystore
#/bin/cp /srv/tomcat6/.keystore ./${DATE}/.keystore

echo "Backing up xwiki configuration"
/bin/cp ${DEPLOYDIR}/WEB-INF/hibernate.cfg.xml ./${DATE}/hibernate.cfg.xml
/bin/cp ${DEPLOYDIR}/WEB-INF/xwiki.cfg ./${DATE}/xwiki.cfg
/bin/cp ${DEPLOYDIR}/WEB-INF/xwiki.properties ./${DATE}/xwiki.properties

#Backup Deploy Context
echo "Backing UP deploy Context"
#/bin/tar -C ${DEPLOYDIR}/../ -zcf ./${DATE}/xwiki.tar.gz xwiki

/bin/tar -C ${DEPLOYDIR}/../ -zcf ./${DATE}/xwiki.tar.gz xwiki


echo "DONE"