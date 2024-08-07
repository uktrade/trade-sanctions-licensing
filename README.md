# apply-for-a-licence
Apply for a licence service :)

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

### 6. Apply migrations to the database
Run the following command to apply migrations to the database:
```
invoke migrate
```

### 7. Run the web server
After following the setup, use the following to run the web app

`invoke runserver --port-number <port_number>`

e.g.
`invoke runserver --port-number 28000`

Navigate to either `apply-for-a-licence:<port_number>` or `view-a-licence:<port_number>` in your browser to see the application.

## Useful commands
### Django
Along with the above runserver command, while developing on the project, \
the following will be handy when making changes to the db model:\
`invoke makemigrations`\
`invoke migrate`

### Dependencies
To add a new dependency to the project, use the following command:\
`pipenv install <package-name>`
