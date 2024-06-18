from typing import Any

from invoke import task


@task
def test(context: Any) -> None:
    context.run("pipenv run pytest tests/")


@task
def unit_tests(context: Any) -> None:
    context.run("pipenv run pytest tests/test_unit")


@task
def frontend_tests(context: Any) -> None:
    context.run("pipenv run pytest tests/test_frontend")


@task
def makemigrations(context: Any) -> None:
    print("Running manage.py makemigrations")
    context.run(f"pipenv run python django_app/manage.py makemigrations")


@task
def migrate(context: Any) -> None:
    print("Running manage.py migrate")
    base_command = f"pipenv run python django_app/manage.py migrate"
    context.run(base_command)


@task
def runserver(context: Any, port_number: int = 8000) -> None:
    context.run(f"pipenv run python django_app/manage.py runserver {port_number}", hide=False, pty=True)


@task
def createsuperuser(context: Any) -> None:
    context.run("pipenv run python django_app/manage.py createsuperuser", hide=False, pty=True)


@task
def collectstatic(context: Any) -> None:
    context.run("pipenv run python django_app/manage.py collectstatic --no-input", hide=False, pty=True)


@task
def black(context: Any, directory: str = ".") -> None:
    print("Running black formatting")
    context.run(f"pipenv run black {directory}")


@task
def mypy(context: Any, module: str = "django_app") -> None:
    context.run(f"mypy {module}", hide=False, pty=True)
