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
  + [Testing](#running-the-tests)


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
pipenv install --dev
```
Now we need to activate the virtual environment:
```
pipenv shell
```

### Installing direnv (optional)
We use direnv to automatically load in certain environment variables into your shell. You can install it with homebrew:
```
brew install direnv
```

After installing direnv, you need to add the following to your shell profile:
If using bash:
```
eval "$(direnv hook bash)"
```
If using zsh:
```
eval "$(direnv hook zsh)"
```

Then you need to allow direnv to load the .env file in the project directory:
```
direnv allow
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

### 6. Install libmagic
The project uses the python-magic library to determine the file type of uploaded files. This library requires the libmagic library to be installed on your system. You can install it with the following command:
```
brew install pipenv
```


### 7. Apply migrations to the database
Run the following command to apply migrations to the database:
```
invoke migrate
```

### 8. Run the web server
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

### Updating the list of sanctions regimes
We store the list of Sanction regimes in a private git submodule located in `django_app/sanctions_regimes`.
The first time you clone the repo, you may need to initialise the submodule:
```
git submodule update --init
```
If this list has changed, you can update it from the latest version of the submodule by running the following command:
```
git submodule update --remote --merge
```

### Running the tests
To run unit tests:
```
invoke unittests
```

To run the frontend tests (more documentation can be found in the tests/test_frontend/README.md):
```
invoke frontendtests
```

### Accessing the viewer portal

The first time accessing the viewer portal you will automatically be logged in as `vyvyan.holland@email.com` through the
mock Staff SSO server. This user will by default not be able to access the viewer portal as `is_active` is set to False in the DB.

Create a superuser with `pipenv run django_app/manage.py createsuperuser` and log in to the admin panel (`http://view-a-licence:8000/admin`) with the superuser credentials.

Go to the User model and set `is_active` to True for the `vyvyan.holland@email.com` user to access the viewer portal.
