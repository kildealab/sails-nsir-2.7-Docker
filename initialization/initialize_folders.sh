#!/bin/bash
# the value af DATA_FOLDER should be in sync with the .yaml file for mariadb and opalquestionnairesdb services

DATA_FOLDER=/mnt/Data/dockerstorage/SaILS-2/
mkdir -p $DATA_FOLDER/mariadb_data
mkdir -p $DATA_FOLDER/redis_data
mkdir -p $DATA_FOLDER/sails_nsir_data/logs
mkdir -p $DATA_FOLDER/sails_nsir_data/media/files
mkdir -p $DATA_FOLDER/sails_nsir_data/static
mkdir -p $DATA_FOLDER/sails_nsir_data/php_emr
echo "The data folder was created here: $DATA_FOLDER"
