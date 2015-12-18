from flask import request, redirect, url_for, render_template, flash, abort, g
from flask_peewee.utils import get_object_or_404, object_list, PaginatedQuery
from flask.ext.bouncer import requires, ensure
from app import app,db
from auth import auth
from models import *
from datetime import datetime,timedelta
from bouncer import can
from bouncer.constants import *

@app.route('/', methods=['GET'])
@auth.login_required
def homepage():
    teams = [t for t in Team.select() if g.user.can(READ,t)]
    if not teams:
        abort(404)
    current_team = get_object_or_404(Team, Team.id == int(
        request.args.get('t'))) if request.args.has_key('t') else teams[0]

    ensure(READ,current_team)

    users = [u for u in User.select().where(User.team == current_team, User.active == True) if g.user.can(READ,u)]
    return render_template("index.html", teams=teams, users=users, active_team=current_team)

def has_score(scores):
    for score in scores:
        if score.user == g.user:
            return True
    return False


@app.route('/users/<int:user_id>', methods=['GET'])
@auth.login_required
def user_detail(user_id):
    teams = [t for t in Team.select() if can(auth.get_logged_in_user(),READ,t)]
    user = get_object_or_404(User, User.id == user_id)
    ensure(READ,user)
    scores = Score.select().where(Score.user == user).order_by(Score.created_at.desc())
    users = [u for u in User.select().where(User.team == user.team) if can(auth.get_logged_in_user(),READ,u)]
    pq = PaginatedQuery(scores, 20)
    last_date = datetime.now() - timedelta(days=5)
    return render_template("index.html", active_user=user, teams=teams, users=users, pagination=pq, page=pq.get_page(), active_team = user.team, weeks = [w for w in Week.select().where(Week.end > last_date) if not has_score(w.score_set)])

@app.route('/users/<int:user_id>/score', methods=['POST'])
@auth.login_required
def save_score(user_id):
    user = get_object_or_404(User, User.id == user_id)
    week = Week.get(Week.id==int(request.form.get("week")))
    ensure(EDIT,user)
    Score.create(
        user = user,
        self_score = request.form.get("score"),
        week_start = week.start,
        week_end = week.end,
        week = week,
        self_memo = request.form.get("self_memo")
        )

    return redirect(url_for('user_detail',user_id=user_id))

@app.route('/users/<int:user_id>/score/<int:score_id>/edit', methods=['GET'])
@auth.login_required
def edit_score(user_id,score_id):
    teams = [t for t in Team.select() if can(auth.get_logged_in_user(),READ,t)]
    user = get_object_or_404(User, User.id == user_id)
    score = get_object_or_404(Score, Score.id == score_id)
    ensure(EDIT,score)
    users = [u for u in User.select().where(User.team == user.team) if can(auth.get_logged_in_user(),READ,u)]
    return render_template("score.html", active_user=user, teams=teams, users=users, active_team = user.team, score=score)

@app.route('/users/<int:user_id>/score/<int:score_id>', methods=['GET'])
@auth.login_required
def show_score(user_id,score_id):
    teams = [t for t in Team.select() if can(auth.get_logged_in_user(),READ,t)]
    user = get_object_or_404(User, User.id == user_id)
    score = get_object_or_404(Score, Score.id == score_id)
    ensure(READ,user)
    users = [u for u in User.select().where(User.team == user.team) if can(auth.get_logged_in_user(),READ,u)]
    return render_template("score_detail.html", active_user=user, teams=teams, users=users, active_team = user.team, score=score)

@app.route('/users/<int:user_id>/score/<int:score_id>', methods=['POST'])
@auth.login_required
def update_score(user_id,score_id):
    with db.database.transaction():
        score = get_object_or_404(Score, Score.id == score_id)
        ensure(EDIT,score)
        score.rater = auth.get_logged_in_user()
        score.score = request.form.get("score")
        score.memo = request.form.get("memo")
        score.save()
        ScoreHistory.create(
            rater = auth.get_logged_in_user(),
            score = score,
            history = request.form.get("score")
            )
        Score.get_or_create(
            user = g.user,
            week = score.week,
            week_start = score.week_start,
            week_end = score.week_end
            )
    return redirect(url_for('user_detail',user_id=user_id))

@app.route('/settings', methods=['GET'])
@auth.login_required
def user_setting():
    return render_template("profile.html")

@app.route('/users', methods=['POST'])
@auth.login_required
def update_user():
    g.user.email = request.form.get("email")
    g.user.full_name =request.form.get("full_name")
    g.user.set_password(request.form.get("password"))
    g.user.save()
    return redirect(url_for('user_setting'))