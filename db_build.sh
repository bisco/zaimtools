#!/bin/bash -x


#---------------------#
# usage
#---------------------#
function usage {
    echo "usage: $0 YYYY-MM-DD"
}

#---------------------#
# configuration
#---------------------#
DB_NAME=zaim.db


#---------------------#
# main
#---------------------#
if [ $# -ne 1 ]; then
    usage
    exit 1
fi

source bin/activate

rm ${DB_NAME}
./dbgen.py
./zaimapi.py $1
