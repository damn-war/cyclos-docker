# cyclos-docker

In this repository, a docker container for the users synchronization at the FSTL is provided.
The user synchronization is implemented in Python by using the API.

## user sync container image
 
### Get the image

There are two options to get the container image.
1. Pulling the image from Dockerhub via:\
   ```docker pull damnwar/cyclos-docker:latest```
2. Build the image yourself using the provided Dockerfile via:\
   ```docker build <PATH_TO_DOCKERFILE>```

### Usage

#### What does the Container do?

There are 2 folder provided to tyhe container as volumes.
One folder for the user to be imported into the FSTL Cyclos.
One folder, where the user data are exported.

It is expected, that there is at least one json file in the import folder.
The Container does the following:
- iterate over all json files in import folder
- iterate over all users in a json file
- check if the user is a privileged one (via some files provided in an extra mount)
- check if the user is present in an corresponding export file
- check if the user is present in Cyclos
- create user if necessary
- write some user data to export files in export folder

#### Two options of usage

The Container can be started via docker or docker compose.

To start the container via docker, run a statement like:\
```docker run -v ./data/import:/import -v ./data/export:/export -v ./data/privileged_members:/privileged_members -e FSTL_CYCLOS_ADMIN_USERNAME=<ADMIN_USERNAME> -e FSTL_CYCLOS_ADMIN_PASSWORD=<ADMIN_PASSWORD> -e IMPORT_FOLDER_PATH=/import -e EXPORT_FOLDER_PATH=/export -e PRIVILEGED_MAPPING_FOLDER=/privileged_members cyclos-docker```\
As can be seen, there must be passed some information to the docker container:
- import volume
- export volume
- privileged users volume
- admin username to interact with the API
- admin password to interact with the API
- import volume path in container as environment variable
- export volume path in container as environment variable
- privileged users volume path in container as environment variable

This can be seperated into the docker compose yaml file and an .env file for simpler usage.
You can find a template of the env var file and a docker compose file in the repo.
In the docker-compose.yml you can choose if you want to build the container by yourself or if you want to pull from Dockerhub.
After cloning this repo, defining the required env vars, volumes and have the list of privileged users (ask me) in the correct location, simply run
`docker compose up`


## Advertisement Notification Container

to be done

## Get Mail Adresses Container

to be done