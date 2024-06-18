# apply-for-a-licence
Apply for a licence service

## Setup
The project requires Python 3.12. Backing services are provided by Docker whilst the web app itself is ran as a normal process with Pipenv.

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

### 5. Run the web server
After following the setup, use the following to run the web app

`invoke runserver`

Django will provide the local url which should be http://127.0.0.1:8000/, navigate to this in your browser to see through the prototype.

## Useful commands
### Django
Along with the above runserver command, while developing on the project, \
the following will be handy when making changes to the db model:\
`invoke makemigrations`\
`invoke migrate`

### Dependencies
To add a new dependency to the project, use the following command:\
`pipenv install <package-name>`
