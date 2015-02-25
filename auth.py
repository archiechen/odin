from flask_peewee.auth import Auth
from app import app, db
from models import User
from flask.ext.bouncer import requires, ensure, Bouncer
from bouncer import authorization_method
from bouncer.constants import *


auth = Auth(app, db, user_model=User)
bouncer = Bouncer(app)
@bouncer.authorization_method
@authorization_method
def define_authorization(user, they):
    if user.is_manager:
        they.can(READ, ALL)
    else:
        def is_self_scored(score):
            return score.user==user or score.history_set.count()>0 or score.user.is_team_leader
        they.can(READ, 'Score', is_self_scored)
        they.can(READ, 'Team', id = user.team.id)
        they.cannot(MANAGE, 'User', id = user.id)
        they.can(EDIT, 'User', id = user.id)

    def is_team_leader(user):
        return user.is_team_leader

    they.cannot(EDIT, 'User', is_team_leader)
    they.can(READ, 'User', id = user.id)

    def is_leader_of_user(u):
        for leadership in u.leaders:
            if user==leadership.leader.leader:
                return True
        return False
    they.can(READ, 'User', is_leader_of_user)

    def is_leader_of_score(score):
        for leadership in score.user.leaders:
            if user==leadership.leader.leader:
                return True
        return False
    they.can(EDIT, 'Score', is_leader_of_score)

    for team_leader in user.lead_teams:
        they.can(MANAGE, 'Team', id = team_leader.team.id)

        

