
# WebURBS

[![Validate Format & Build](https://github.com/tum-ens/weburbs/actions/workflows/build.yml/badge.svg)](https://github.com/tum-ens/weburbs/actions/workflows/build.yml)
[![Latest Docker Image](https://github.com/tum-ens/weburbs/actions/workflows/docker.yml/badge.svg)](https://github.com/tum-ens/weburbs/actions/workflows/docker.yml)

WebURBS provides an interactive Webapp to configure
a URBS simulation and display its results.
The following sheets of URBS are currently supported:
Sites, Processes, Commodities, Demand, SupIm, Storage.
For Processes, Commodities and Demand we provide some default data
that the user can choose.
It is also possible to configure the [default data](#default-data) provided for the user.
For SupIm the Solar and Wind data can be queried from [Renewable Ninja](https://www.renewables.ninja/) for the selected position.
Additionally, the user is able to [upload](#upload-timeseries) its own timeseries.


## Upload timeseries

Currently only JSON is supported for uploading timeseries.
The JSON needs to contain exactly one list with 8760 numbers.

## Advanced Mode

## Deploy Application

The application is designed to run inside a docker container behind a reverse proxy.
An example for a working docker compose can be found [here](docker-compose.yaml).
It uses nginx as reverse proxy publishing the application to port 9000 on localhost.
To change this edit the exposed port for the reverse proxy and adjust the ORIGINS domain for the backend.
This reverse proxy is currently configured without HTTPS, never use this for production as is!
You can find below how to disable HTTPS mode for the backend.
Don't forget to change the SECRET_KEY before using it in production.

In order to get the application running you need to get yourself an API key for [Renewable Ninja](https://www.renewables.ninja/).
Insert it for "$RN_KEY" for the backend.

For backend only the path `/api` should be made available to the outside.
The path `/callback` needs to be reachable from the optimizer to report the results.
Don't publish `/callback` to the outside, as it is not protected.


The following list contains the available environment variables for the application.
Backend:

|         Key          |                                                              Description                                                               |            Example             |
|:--------------------:|:--------------------------------------------------------------------------------------------------------------------------------------:|:------------------------------:|
|      SECRET_KEY      |                                                       Secret key used by Django                                                        |           change_me            |
|         URBS         |                                            Address where the backend can find the optimizer                                            | http://optimizer:5000/simulate |
|    URBS_CALLBACK     |                                            Address where the optimizer can find the backend                                            |      http://backend:8000       |
| DJANGO_ALLOWED_HOSTS | All the hosts that the backend accepts. Hosts can be separated by comma, also needs to contain the internal address for the optimizer. |      your.domain,backend       |
|       ORIGINS        |                 Contains your domain again. Does not need to contain the internal address for the optimizer this time.                 |      https://your.domain       |
|        RN_KEY        |                                                      API Key for Renewable Ninja                                                       |         gibberishtoken         |
|      SQL_ENGINE      |                                                       Selected type of database                                                        | django.db.backends.postgresql  |
|     SQL_DATABASE     |                                                          Name of the database                                                          |              urbs              |
|       SQL_USER       |                                                          User of the database                                                          |             myuser             |
|     SQL_PASSWORD     |                                                         Password for the user                                                          |             s3cr3t             |
|       SQL_HOST       |                                                        Address of the database                                                         |               db               |
|       SQL_PORT       |                                                          Port of the database                                                          |              5432              |

Frontend:

|       Key       |                                      Description                                       |       Example       |
|:---------------:|:--------------------------------------------------------------------------------------:|:-------------------:|
| VUE_APP_API_URL | The domain where the client finds the backend. Should be equal to your default domain. | https://your.domain |

### Default Data

On startup the backend reads the configuration of the default data into its database.
This default data can be selected by the user and added into their projects.
It is possible to provide default commodities, demands, processes and storage.
Examples for default configurations can be found in [backend/config](backend/config).
Every file inside this folder is read on startup and used as default data.
Inside the docker image you can override this configuration by mounting your own config folder
for the backend using
```
volumes:
  - ./yourfolder:/app/config
```

An explanation for the form of the default data can be found [here](docs/Config.md).

## Programmers Guide

You are here to bring in new features or fix some not existing bugs?
Here you should find a guide on how to get the application up and running
on your local machine to start developing.

The following description is made for Linux.
For other operating systems it can differ.

### Frontend

The frontend is based on Typescript using the framework [Vue.js](https://vuejs.org/).
You can find all the files belonging to it inside of [frontend](frontend).
Before diving into it, the [Vue tutorial](https://vuejs.org/tutorial) could be beneficial.
To get the frontend running you need to have Node.js and a package manager like npm/pnpm/yarn installed.
The following example tutorial will use npm.

Before starting the server we need to install all the required packages.
These can be found inside [package.json](frontend/package.json) and be installed with the following command.
```bash
# Get into the correct folder
cd frontend
# Install all necessary dependencies
npm install
```

Now we can already start the server using the following.
```bash
npm run dev
```
The server should now be running under [localhost:8080](http://localhost:8080).

### Backend

The backend is using Python with [Django](https://www.djangoproject.com/) as framework.
You can find all the files belonging to it inside of [backend](backend).
If you don't have Python installed take a look at the [official Website](https://www.python.org/).
All the requirements for python can be found in [requirements.txt](backend/requirements.txt).
We now create a fresh virtual environment and install them.
You should need to do this step only once.

```shell
# Navigate into backend folder
cd backend
# Create virtual environment
python -m venv urbs-venv
# Upgrade pip and install requirements
./urbs-env/bin/python -m pip install --upgrade pip
./urbs-env/bin/pip install --upgrade pip 
./urbs-env/bin/pip install -r requirements.txt
```

We can use some local variables to configure the application
to put it into the Debug mode and provide a Renewable Ninja api key.
Create a `.env` file inside the backend folder with all the needed variable.
You can use the following file:
```dotenv
RN_KEY=1408b994667748f3aff7aff50a56759c3e85cb89
DJANGO_DEBUG=True
```

To read in the `.env` file and have them as environment variables you can use the following command.
(You might need to install the package dotenv on Ubuntu or dot on Fedora.)
```bash
. .env
```

Now we need to initialize the database.
This is done with the following command.
```bash
./urbs-env/bin/python manage.py migrate
```

Now we can fill the database with our default config.
This step needs to be repeated when the config is changed.
```bash
./urbs-env/bin/python manage.py load_config
```

Finally, we can now run the server.
As long as nothing is changed this should be the only step
that needs to be repeated.
```bash
./urbs-env/bin/python manage.py runserver
```
The server should now be running under [localhost:8000](http://localhost:8000).

### Database

By default, the backend will use a SQlite as database.
As an alternative you can use a local database or use the following
docker compose to create a postgres database in a docker container:
```yaml
service:
  db:
    image: postgres:17
    container_name: weburbs-db
    environment:
      - POSTGRES_USER=urbs
      - POSTGRES_PASSWORD=urbs
      - POSTGRES_DB=urbs
    ports:
      - "5432:5432"
```

To use this database we need to add the following code to our `.env` file.
(Don't forget to reread the environment variables after updating with `. .env`.)
```dotenv
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=urbs
SQL_USER=urbs
SQL_PASSWORD=urbs
SQL_HOST=localhost
SQL_PORT=5432
```

### Formatter

Inside the [CI pipeline](.github/workflows/build.yml) the format and types of all files are checked.
To prevent failing pipelines the code should always be formatted and checked before pushing.

For the backend the linter [Ruff](https://github.com/astral-sh/ruff) is used.
It can be installed via pip: `pip install ruff` and used with the following commands
inside the [backend](backend) folder.
```bash
ruff format
ruff check .
```

For the frontend prettier and eslint is used.
They have already been installed by the first setup of the frontend.
You should use the following three commands to format and verify your code.
```bash
npm run format
npm run lint
npm run type-check
```

Now your code should be ready to be pushed!

### Versioning

There is another [pipeline](.github/workflows/docker.yml) responsible for building docker images.
The build is triggered when adding a tag to a commit.
Then the images for the frontend and backend are being build and published on GitHub.
The tag needs to be of the form `v1.2.3`.
This tags the images with following versions: `latest`, `1`, `1.2`, `1.2.3`.
