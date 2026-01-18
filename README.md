# Django REST Skeleton

This is a starter that can be used to bootstrap Django REST API projects.


## Prerequisites

- Docker
- Docker compose
- python 3.12 or above
- python venv
- pip

## Getting Started

Adjust User model as needed. It extends AbstractUser, which is default User model used by Django.
If default is enough for your application needs, then remove custom User model.

Run ``make build`` to build a project for the first time (uncomment collectstatic line if you will be using admin).

Run ``make up`` to start containers (by default they won't run in detached mode. Add -d in MakeFile up command, if you wish them to).

That is it, enjoy building your new application.