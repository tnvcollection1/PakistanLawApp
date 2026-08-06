#!/bin/bash
# Chain headnotes import for all remaining years
# Run: nohup bash /opt/pls/backend/scripts/import_headnotes_chain.sh > /tmp/headnotes_chain.log 2>&1 &

PYTHON="/opt/pls/backend/venv/bin/python3"
SCRIPT="/opt/pls/backend/scripts/import_headnotes.py"

for YEAR in 2023 2022 2021 2020 2019 2018 2017 2016 2015 2014 2013 2012 2011 2010 2009 2008 2007 2006 2005 2004 2003 2002 2001 2000 1999 1998 1997 1996 1995 1994 1993 1992 1991 1990; do
    echo "=============================="
    echo "Starting year: $YEAR at $(date)"
    echo "=============================="
    $PYTHON $SCRIPT --year $YEAR --batch 5000
    echo "Year $YEAR complete at $(date)"
    echo ""
    sleep 5
done

echo "ALL YEARS COMPLETE at $(date)"
