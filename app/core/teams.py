import math
from flask import (
    render_template,
    request,
    flash,
    url_for,
    abort,
    redirect,
)
from sqlalchemy.sql import text
from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectField, IntegerField, HiddenField
from wtforms import validators as vl

from app import db
from .views import bp_core
from .helpers import int_safe, champ_types_dict
from .constants import AlertType

@bp_core.route('/teams/list', endpoint='teams_list', methods=['GET'])
def teams_list():

    filter_year = int_safe(request.args.get("year", None) or 0, 0)

    page_size = 40;
    page_num = max(int_safe(request.args.get('page', 1) or 1, 1), 1)

    query_comps = [
        "SELECT * FROM teams WHERE",
        "teams.year = :year AND" if filter_year != 0 else "",
        "teams.teamtag != ''",
        "ORDER BY teamtag",
        f"LIMIT {(page_num - 1) * page_size}, {page_size}"
    ]
    stmt = text(" ".join(query_comps))
    rows = db.session.execute(stmt, {'year': filter_year}).fetchall()

    count_stmt = text(" ".join([
        "SELECT count(teamtag) FROM teams",
        "WHERE teams.year = :year" if filter_year != 0 else "", 
    ]))
    count_result = db.session.execute(count_stmt, {'year': filter_year}).fetchone()
    total_pages = math.ceil(count_result[0] / page_size)

    return render_template(
        'ui/teams_list.html',
        teams=rows,
        min_year=2014,
        max_year=2019,

        filter_selected_year=filter_year,
        current_page=page_num,
        total_pages=total_pages,
        render_page_start=max(1, page_num - 2),
        render_page_end=min(total_pages, page_num + 2),
    )


class AddTeamForm(FlaskForm):
    teamtag             = StringField("Team Tag",   validators=[vl.InputRequired()])
    year                = IntegerField("Year",      validators=[vl.InputRequired(), vl.NumberRange(min=1800)])

    season              = SelectField("Season",     validators=[vl.InputRequired()], 
                            choices=['Summer', 'Spring', 'Fall', 'Autumn'])

    player_top          = StringField("Top",        validators=[vl.InputRequired()])
    player_jungle       = StringField("Jungle",     validators=[vl.InputRequired()])
    player_mid          = StringField("Mid",        validators=[vl.InputRequired()])
    player_adc          = StringField("ADC",        validators=[vl.InputRequired()])
    player_support      = StringField("Support",    validators=[vl.InputRequired()])

@bp_core.route('/team/add', endpoint='team_add', methods=['GET', 'POST'])
def team_add():
    form = AddTeamForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            
            # Add the team
            stmt = text("""
                INSERT INTO teams VALUES
                (:teamtag, :year, :season, :player_top, :player_jungle, :player_mid, :player_adc, :player_support)
            """);

            db.session.execute(stmt, {
                'teamtag':          form.teamtag.data,
                'year':             form.year.data,
                'season':           form.season.data,
                'player_top':       form.player_top.data,
                'player_jungle':    form.player_jungle.data,
                'player_mid':       form.player_mid.data,
                'player_adc':       form.player_adc.data,
                'player_support':   form.player_support.data,
            })

            flash("Team added successfully", AlertType.Success)
        else:
            flash("Invalid form data", AlertType.Error)

        return redirect(url_for('core.team_add'))

    return render_template(
        'ui/team_add.html',

        form=form
    )

class UpdateTeamForm(FlaskForm):
    teamtag             = StringField("Team Tag",   validators=[vl.InputRequired()])
    year                = IntegerField("Year",      validators=[vl.InputRequired(), vl.NumberRange(min=1800)])

    season              = SelectField("Season",     validators=[vl.InputRequired()], 
                            choices=['Summer', 'Spring', 'Fall', 'Autumn'])

class DeleteTeamForm(FlaskForm):
    teamtag = HiddenField("Team Tag",   validators=[vl.InputRequired()])


@bp_core.route('/team/update/<name>', endpoint='team_update', methods=['GET', 'POST'])
def team_update(name):
    form = UpdateTeamForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            
            # Add the team
            stmt = text("""
                UPDATE teams
                SET 
                    teamtag = :teamtag , 
                    year = :year , 
                    season = :season
                WHERE teamtag = :orignal_tag ;
            """);

            db.session.execute(stmt, {
                'orignal_tag': name,

                'teamtag':  form.teamtag.data,
                'year':     form.year.data,
                'season':   form.season.data,
            })

            flash("Team updated successfully", AlertType.Success)
            return redirect(url_for('core.teams_list'))
        else:
            flash("Invalid form data", AlertType.Error)
            return redirect(url_for('core.team_update', name=name))


    select_team_stmt = text("SELECT count(teamtag) FROM teams WHERE teamtag = :teamtag ;")
    count_row = db.session.execute(select_team_stmt, {'teamtag': name}).fetchone()
    if count_row[0] == 0:
        abort(404)

    form.teamtag.data = name

    return render_template(
        'ui/team_update.html',

        form=form,
        teamtag=name,
        delete_form=DeleteTeamForm()
    )

@bp_core.route('/team/delete', endpoint='team_delete', methods=['POST'])
def team_delete():
    form = DeleteTeamForm()

    if form.validate_on_submit():
        # Add the team
        stmt = text("""
            DELETE FROM teams WHERE teams.teamtag = :teamtag ;
        """);

        db.session.execute(stmt, {
            'teamtag': form.teamtag.data
        })

        flash("Team deleted successfully", AlertType.Success)
    else:
        flash("Invalid form data", AlertType.Error)

    return redirect(url_for('core.teams_list'))


@bp_core.route('/team/selections', endpoint='team_selections', methods=['GET'])
def team_selections():

    filter_year = int_safe(request.args.get("year", 0) or 0, 0)
    filter_teamtag = request.args.get("teamtag", '')
    filter_ctype = request.args.get("ctype", '')

    db_query_ctype = champ_types_dict.get(filter_ctype, 'Top')

    show_results = db_query_ctype != '' and filter_teamtag and filter_year > 0

    query_comps = [
        f"SELECT picks.blue{db_query_ctype}Champ",
        "FROM picks, teams",
        "WHERE picks.blueteamtag = teams.teamtag and teams.year = :year and teams.teamtag = :teamtag",
        "UNION",
        f"SELECT picks.red{db_query_ctype}Champ",
        "FROM picks, teams",
        "WHERE picks.redteamtag = teams.teamtag and teams.year = :year and teams.teamtag = :teamtag ;",
    ]

    if show_results:
        stmt = text(" ".join(query_comps))

        rows = db.session.execute(stmt, {
            'year': filter_year,
            'teamtag': filter_teamtag
        }).fetchall()
    else:
        rows = []

    return render_template(
        "ui/team_selections.html",

        show_results=show_results,
        champ_types=list(champ_types_dict.keys()),

        filter_ctype=db_query_ctype,
        filter_year='' if filter_year == 0 else filter_year,
        filter_teamtag=filter_teamtag,

        rows=rows
    )


def clamp(num, min_num, max_num):
    if num > max_num:
        return max_num
    if num < min_num:
        return min_num

    return num

@bp_core.route('/team/bans', endpoint='team_bans', methods=['GET'])
def team_bans():

    filter_teamtag = request.args.get("teamtag", '').strip()
    filter_ban_num = clamp(int_safe(request.args.get("ban_num", 1), 1), 1, 5)

    show_results = filter_teamtag != ''

    row = ["", ""]

    if show_results:
        ban_col_name = f"ban{filter_ban_num}"
        stmt = text(" ".join([
            f"SELECT {ban_col_name}, COUNT({ban_col_name})",
            "FROM bans, picks",
            "where picks.blueteamtag = :teamtag and picks.address = bans.address",
            f"GROUP BY {ban_col_name}",
            "UNION",
            f"SELECT {ban_col_name}, COUNT({ban_col_name})",
            "FROM bans, picks",
            "where picks.redteamtag = :teamtag and picks.address = bans.address",
            f"GROUP BY {ban_col_name}",
            f"ORDER BY COUNT({ban_col_name}) DESC",
            "limit 1;",
        ]))

        row = db.session.execute(stmt, {
            'teamtag': filter_teamtag
        }).fetchone()

    return render_template(
        "ui/team_bans.html",

        show_results=show_results,
        filter_teamtag=filter_teamtag,
        filter_ban_num=filter_ban_num,
        row=row
    )


@bp_core.route('/team/players', endpoint='team_players', methods=['GET'])
def team_players():

    filter_teamtag = request.args.get("teamtag", '').strip()
    filter_champ_name = request.args.get("champ_name", '').strip()
    filter_ctype = request.args.get("ctype", '')

    db_query_ctype = champ_types_dict.get(filter_ctype, 'Top')

    show_results = filter_teamtag and filter_champ_name

    if show_results:
        stmt = text(" ".join([
            f"SELECT matches.year, matches.season, matches.type, matches.league, matches.BlueTeamTag, picks.blue{db_query_ctype}Champ, matches.redTeamTag, picks.red{db_query_ctype}Champ",
            "FROM matches, picks",
            f"WHERE matches.address = picks.address AND matches.blueTeamTag = :teamtag AND picks.blue{db_query_ctype}Champ = :plr_name",
            "UNION",
            f"SELECT matches.year, matches.season, matches.type, matches.league, matches.BlueTeamTag, picks.blue{db_query_ctype}Champ, matches.redTeamTag, picks.red{db_query_ctype}Champ",
            "FROM matches, picks",
            f"WHERE matches.address = picks.address AND matches.redTeamTag = :teamtag AND picks.red{db_query_ctype}Champ = :plr_name ;",
        ]))

        rows = db.session.execute(stmt, {
            'plr_name': filter_champ_name,
            'teamtag': filter_teamtag,
        }).fetchall()

    else:
        rows = []

    return render_template(
        "ui/team_players.html",

        rows=rows,

        filter_teamtag=filter_teamtag,
        filter_champ_name=filter_champ_name,
        filter_ctype=db_query_ctype,

        champ_types=list(champ_types_dict.keys())
    )

