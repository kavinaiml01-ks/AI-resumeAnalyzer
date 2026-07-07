from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User          # noqa
from .recruiter import Recruiter  # noqa
from .job import Job             # noqa
from .resume import Resume       # noqa
from .application import Application  # noqa
