#!/bin/sh

if [ $? -gt 0 ]
then
	ext="$1"
else
	ext=""
fi

vdate="`date`"
revision="`git rev-parse HEAD`"

cat <<ENDL >version.py
builddate="`date`"
revision="`git rev-parse HEAD`"

ENDL

