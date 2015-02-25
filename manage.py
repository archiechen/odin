# -*- coding: utf-8 -*-
import os
import sys

from flask.ext.script import Manager, Command, Option
from app import app,db
from models import *
from admin import admin
from auth import auth
from views import *
from playhouse.migrate import *
import datetime

manager = Manager(app)

@manager.command
def migrator():
    migrator = PostgresqlMigrator(db.database)

    text_field = TextField(null=True)

    with db.database.transaction():
        migrate(
            migrator.add_column('score', 'self_memo', text_field),
        )

@manager.command
def generate_week():
    today = datetime.date.today()
    week_of_year = today.isocalendar()[1]
    weekday = today.weekday()
    start_delta = datetime.timedelta(days=weekday)
    end_delta=datetime.timedelta(days=6)
    start_of_week = today - start_delta
    end_of_week = start_of_week+end_delta

    Week.create(
            name=u"%d年第%d周（%s to %s）" % (today.year,week_of_year,start_of_week.strftime("%Y/%m/%d"),end_of_week.strftime("%Y/%m/%d")),
            start = start_of_week,
            end = end_of_week
        )
 
class GunicornServer(Command):
    """Run the app within Gunicorn"""
 
    def get_options(self):
        from gunicorn.config import make_settings
 
        settings = make_settings()
        options = (
            Option(*klass.cli, action=klass.action)
            for setting, klass in settings.iteritems() if klass.cli
        )
        return options
 
    def run(self, *args, **kwargs):
        run_args = sys.argv[2:]
        run_args.append('manage:app')
        os.execvp('/opt/apps/odin/bin/gunicorn', [''] + run_args)

manager.add_command("gunicorn", GunicornServer())


if __name__ == "__main__":
    Team.create_table(fail_silently=True)
    User.create_table(fail_silently=True)
    Score.create_table(fail_silently=True)
    ScoreHistory.create_table(fail_silently=True)
    TeamLeader.create_table(fail_silently=True)
    Governor.create_table(fail_silently=True)
    Week.create_table(fail_silently=True)
    Leadership.create_table(fail_silently=True)
    admin.setup()
    manager.run()
