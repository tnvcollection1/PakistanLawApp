#!/bin/bash
# Import headnotes chain

cat headnotes.csv | while read line; do
  echo "Importing: $line"
done
