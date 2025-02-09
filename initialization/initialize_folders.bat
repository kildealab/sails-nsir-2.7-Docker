set DATA_FOLDER="C:\Users\***\Documents\data"
md %DATA_FOLDER%\mariadb_data
md %DATA_FOLDER%\redis_data
md %DATA_FOLDER%\sails_nsir_data\logs
md %DATA_FOLDER%\sails_nsir_data\media\files
md %DATA_FOLDER%\sails_nsir_data\static
md %DATA_FOLDER%\sails_nsir_data\php_emr
echo The data folder was created here: %DATA_FOLDER%
