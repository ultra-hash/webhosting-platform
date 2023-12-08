#!/bin/bash

user = 'root'
pass = 'rootpassword'
host = $1
port = 3306

username = $2
password = $3


if [ $# < 3 ]; then
    echo " expecting 3 arguments. Received : $#"
elif [ $# > 3 ]; then
    echo "expecting 3 arguments. Received : $#"
else
    if [ (mysql -u $user -p$pass -h $host -P $port -e "show databases;") ]; then
        echo "working"
    else
        echo "connection failed"
    fi
fi