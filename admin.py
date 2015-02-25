import datetime
from flask import request, redirect

from flask_peewee.admin import Admin, ModelAdmin, AdminPanel
from flask_peewee.filters import QueryFilter

from app import app, db
from auth import auth
from models import *


class UserStatsPanel(AdminPanel):
    template_name = 'admin/user_stats.html'

    def get_context(self):
        last_week = datetime.datetime.now() - datetime.timedelta(days=7)
        signups_this_week = User.select().where(User.join_date > last_week).count()
        return {
            'signups': signups_this_week,
        }

admin = Admin(app, auth, branding='Example Site')


class TeamAdmin(ModelAdmin):
    columns = ('name',)


class ScoreAdmin(ModelAdmin):
    columns = ('user', 'week', 'week_start','week_end','score')
    exclude = ('created_at',)


class TeamLeaderAdmin(ModelAdmin):
    columns = ('leader', 'team')


class LeadershipAdmin(ModelAdmin):
    columns = ('leader', 'employee')


class GovernorAdmin(ModelAdmin):
    columns = ('user',)

class WeekAdmin(ModelAdmin):
    columns = ('name','start','end')

auth.register_admin(admin)
admin.register_panel('User stats', UserStatsPanel)
admin.register(Team, TeamAdmin)
admin.register(Score, ScoreAdmin)
admin.register(TeamLeader, TeamLeaderAdmin)
admin.register(Governor, GovernorAdmin)
admin.register(Week, WeekAdmin)
admin.register(Leadership, LeadershipAdmin)
