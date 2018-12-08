#!/bin/bash -x


#---------------------------------#
# usage
#---------------------------------#
# Description:
#   This is a script for updating database.
#   Please use this script with cron or another program like cron.
# 
# Before run script:
#   Change WORKDIR to a path to this script and zaim.py, zaimapi.py, gspread.py
#

#---------------------------------#
# configuration
#---------------------------------#
WORKDIR=""
LOGDIR="log"

#---------------------------------#
# main
#---------------------------------#
cd ${WORKDIR}
source bin/activate

if [ -e ${LOGDIR} ]; then
    mkdir ${LOGDIR}
fi

FILENAME=${LOGDIR}/`date +"%Y%m%d%H%M%S"`.log
if [ $( date -d '+1 day' +%d ) -eq 1 ]; then
    ./zaim.py --spreadsheet > $FILENAME 2>&1
else
    ./zaim.py > $FILENAME 2>&1
fi
