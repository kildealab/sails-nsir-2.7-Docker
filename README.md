# **Safety and Incident Learning System (NSIR-RT)** #

This is the repository for the NSIR-RT compatible version of the Safety and Incident Learning System (SaILS). This version, developed at the McGill University Health Centre, incorporates the taxonomy of the Canadian National System for Incident Reporting - Radiation Treatment (NSIR-RT). For the original version of SaILS, developed at the Ottawa Hospital Cancer Centre, please visit: [https://bitbucket.org/tohccmedphys/sails/](https://bitbucket.org/tohccmedphys/sails/).

### The core features offered by SaILS are: ###

1. An incident reporting interface
2. An incident investigation interface
3. Incident tracking functionality
4. A data visualization interface

### Additional features within SaILS include: ###

* An administrator interface
* An email framework (with support for automatic email reminders)
* Framework for connecting SaILS with your electronic medical record (for auto-field population & document retrieval)
* Taskable actions
* Incident templates
* User dashboards
* A robust incident search feature
* Filtered incident lists

### Requirements ###

* [Docker Engine](https://docs.docker.com/) with [compose ](https://docs.docker.com/compose/).

### Installation Instructions ###

1. Clone this repository into your server (this will make a local copy of the repository).
2. Data folder.
   1. Create a data folder on your server. The data folder is used (1) by the mariadb containers to store the database used by opalquestionnairesDB-app,
(2) by redis, (3) by the Django portal (SaILS-app) 
to store static and media files (4) by the webserver (nginx) to store access logs.
   2. Use the following structure:
   data\
   ├── mariadb_data\
   ├── redis_data\
   └── sails_nsir_data\
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── php_emr\
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── logs\
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── media\
   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── static\
   3. Edit the .env_template file with DOCKER_STORAGE=path of the data folder, and rename it to .env

      _Note: You may want to keep the original .env_template files as is for Git update compatibility_

   _Note: You can use the script initialization/initialize_folders.sh (linux) or initialize_folders.bat 
   (Windows) to automatically perform this step. Edit the script with DATA_FOLDER=data folder path_

3. Edit the mariadb/.env_template
- By default, the MARIADB_DATABASE is SaILS_DB and MARIADB_USER=sailsdb.
- MARIADB_PASSWORD and MARIADB_ROOT_PASSWORD should be strong passwords.
- Rename .env \
_Note: You may want to keep the originals .env_template files as is for Git update compatibility_

4. Edit the sails-app/.env_template file.
- DJANGO_SUPERUSER is a user with all privileges to manage the sails-app database.
- Rename to .env
_Note: You may want to keep the original .env_template files as is for Git update compatibility_

5. SaILS configuration.
- Follow the instructions provided in the *SaILS_Installation_Instructions (for Docker).pdf* file included in the source code (in the root directory of the project)
* Please contact us if you have trouble getting the software installed
* Note: The instructions are straightforward, but basic familiarity with Bash and Python will be required to install and configure the software to your needs!

6. Build the docker images:
- In a terminal window, navigate to the cloned repository folder.
- Issue the command: 
```
docker compose build
```
- Wait for the images to be created

### Start the application ###

1. In a terminal window, navigate to the cloned repository folder.
2. Issue the command: 
```
docker compose up
```
3. Wait for the containers to be created\
_Note: to reuse the terminal, you can use (see the Docker documentation for details):_
```
docker compose up -d
```
4. You can use the app locally at http://localhost:8080/ or remotely using the port 8080.\
_Note: The default port is 8080. You can change it in docker-compose.yaml in the nginx services._
5. Use the DJANGO SUPERUSER account (Installation, step 5) to create and manage users.
