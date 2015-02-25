from hashlib import md5
import datetime
from bouncer import authorization_target
from flask_peewee.auth import BaseUser
from peewee import *

from app import db

class Team(db.Model):
    name = CharField()

    def __unicode__(self):
        return self.name

    def get_mean_of_score(self,week_start):
        scores = Score.select().join(User).where(Score.week_start==week_start,User.team==self)
        score_list = [s.get_score() for s in scores if not s.user.is_team_leader or s.user.lead_teams.first().team!=self]
        if score_list:
            return reduce(lambda x, y: x + y, score_list) / float(len(score_list))
        return 0

@authorization_target
class User(db.Model, BaseUser):
    username = CharField()
    password = CharField()
    email = CharField()
    full_name = CharField()
    team =  ForeignKeyField(Team)
    join_date = DateTimeField(default=datetime.datetime.now)
    active = BooleanField(default=True)
    admin = BooleanField(default=False)

    def __unicode__(self):
        return self.full_name

    @property
    def is_manager(self):
        return self.governor.first()

    @property
    def is_team_leader(self):
        return self.lead_teams.count()>0

    def gravatar_url(self, size=80):
        return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
            (md5(self.email.strip().lower().encode('utf-8')).hexdigest(), size)

    def mean_of_score(self):
        mean = Score.select(fn.Avg(Score.score).alias("mean")).where(Score.user==self)
        return mean.first().mean

    def recently_score(self,limit = 5):
        recently = Score.select().where(Score.user==self).order_by(Score.created_at.desc()).limit(limit)
        return [s.get_score() for s in recently]

class TeamLeader(db.Model):
    team = ForeignKeyField(Team,related_name="team_leaders")
    leader = ForeignKeyField(User,related_name="lead_teams")

    def __unicode__(self):
        return "%s - %s" % (self.leader.full_name,self.team.name)

class Leadership(db.Model):
    leader = ForeignKeyField(TeamLeader)
    employee = ForeignKeyField(User,related_name="leaders")


class Governor(db.Model):
    user = ForeignKeyField(User,related_name="governor")

class Week (db.Model):
    name = CharField()
    start = DateField(default=datetime.datetime.now)
    end = DateField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.name

class Score(db.Model):
    user = ForeignKeyField(User,related_name="scores")
    rater = ForeignKeyField(User,null=True)
    week_start = DateField(default=datetime.datetime.now)
    week_end = DateField(default=datetime.datetime.now)
    week = ForeignKeyField(Week)
    score = IntegerField(null=True)
    self_score = IntegerField(default=0)
    memo = TextField(null=True)
    self_memo = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    def get_self_score(self):
        if self.user.is_team_leader:
            return round(self.user.lead_teams.first().team.get_mean_of_score(self.week_start), 2)
        else:
            return self.self_score

    def get_score(self):
        if self.user.is_team_leader:
            team_score=self.user.lead_teams.first().team.get_mean_of_score(self.week_start)
            if team_score and self.score:
                return round(self.score*2 - team_score  if team_score > self.score else team_score, 2)
            else:
                return 0

        else:
            return self.score if self.score else 0


class ScoreHistory(db.Model):
    score = ForeignKeyField(Score,related_name="history_set")
    history = IntegerField()
    rater = ForeignKeyField(User)
    created_at = DateTimeField(default=datetime.datetime.now)

