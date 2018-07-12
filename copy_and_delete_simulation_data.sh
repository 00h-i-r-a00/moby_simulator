#!/bin/bash
folder_to_copy_results=$1
mkdir $folder_to_copy_results
cp -a data/results $folder_to_copy_results
cp -a data/logs $folder_to_copy_results
cp -a data/memory_logs $folder_to_copy_results
cp -a data/seeds $folder_to_copy_results

rm -rf *.json
rm -rf data/results/*
rm -rf data/logs/*
rm -rf data/memory_logs/*
rm -rf data/seeds/*
