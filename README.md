# apply-for-a-licence
Apply for a trade sanctions licence service

* [Setup](#setup)
  + [1. Setting up your virtual environment](#1-setting-up-your-virtual-environment)
  + [2. Installing pre-commit](#2-installing-pre-commit)
  + [3. Setup your local environment variables](#3-setup-your-local-environment-variables)
  + [4. Run the backing services](#4-run-the-backing-services)
  + [5. Add the sites to your hosts file](#5-add-the-sites-to-your-hosts-file)
  + [6. Apply migrations to the database](#6-apply-migrations-to-the-database)
  + [7. Run the web server](#7-run-the-web-server)
* [Useful commands](#useful-commands)
  + [Django](#django)
  + [Dependencies](#dependencies)


## Setup
The project requires Python 3.12. Backing services are provided by Docker whilst the web app itself is run as a normal process with Pipenv.

### 1. Setting up your virtual environment
We use Pipenv to manage our virtual environment, dependencies, and environment variables. You can install it with either of the following commands:
```
# with homebrew
pip install --user pipenv

# OR with homebrew
brew install pipenv
```
Once installed, we need to install the requirements for the project:
```
pipenv install
```
Now we need to activate the virtual environment:
```
pipenv shell
```

### 2. Installing pre-commit
Install the repos pre commit hooks:
```
pre-commit install
```
Set pre-commit to autoupdate:
```
pre-commit autoupdate
```


### 3. Setup your local environment variables
Copy and paste the `env.example` file and rename it to `.env`
```
cp .env.example .env
```

### 4. Run the backing services
Use docker-compose to run the backing services
```
docker-compose up -d
```

### 5. Add the sites to your hosts file
Add the following to your etc/hosts file:
```
127.0.0.1 apply-for-a-licence
127.0.0.1 view-a-licence
```

### 6. Apply migrations to the database
Run the following command to apply migrations to the database:
```
invoke migrate
```

### 7. Run the web server
After following the setup, use the following to run the web app

```
invoke runserver --port-number <port_number>
```

e.g.
```
invoke runserver --port-number 28000
```

Navigate to either `apply-for-a-licence:<port_number>` or `view-a-licence:<port_number>` in your browser to see the application.

## Useful commands
### Django
Along with the above runserver command, while developing on the project,
the following will be handy when making changes to the db model:
```
invoke makemigrations
invoke migrate
```

### Dependencies
To add a new dependency to the project, use the following command:
```
pipenv install <package-name>
```
