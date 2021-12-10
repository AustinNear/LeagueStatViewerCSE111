from flask import (
    render_template,
    request,
)
from sqlalchemy.sql import text

from app import db
from .views import bp_core
from .helpers import champ_types_dict

@bp_core.route('/stats/most-kd', endpoint='misc_most_kd', methods=['GET'])
def most_kd():

    kill_stmt = text("""
        SELECT killer, count(killer) FROM kills
        GROUP BY killer
        ORDER BY count(killer) DESC
        LIMIT 1;
    """)

    death_stmt = text("""
        SELECT victim, count(victim) FROM kills
        GROUP BY victim
        ORDER BY count(victim) DESC
        LIMIT 1;
    """)

    kill_stats = db.session.execute(kill_stmt).fetchone()
    death_stats = db.session.execute(death_stmt).fetchone()

    return render_template(
        'ui/most_kd.html',

        kill_stats=kill_stats,
        death_stats=death_stats
    )


@bp_core.route('/stats/side-wins', endpoint='misc_side_wins', methods=['GET'])
def misc_side_wins():

    stmt = text("""
        SELECT 'blue' as tside, count(*) as wins
        FROM matches
        WHERE bResult = '1'
        UNION
        SELECT 'red' as tside, count(*) as wins
        FROM matches
        WHERE rResult = '1';
    """)

    stats = db.session.execute(stmt).fetchall()

    return render_template(
        'ui/side_wins.html',

        blue_wins=stats[0][1],
        red_wins=stats[1][1]
    )


@bp_core.route('/stats/match-champs', endpoint='misc_match_champs', methods=['GET'])
def misc_match_champs():

    filter_ctype = request.args.get("ctype", '')
    filter_m_addr = request.args.get("match_addr", '')
    filter_side = request.args.get("side", '')

    db_query_ctype = champ_types_dict.get(filter_ctype, 'Top')
    if filter_side != 'blue' and filter_side != 'red':
        filter_side = 'blue'

    show_results = db_query_ctype and filter_m_addr

    if show_results:
        stmt = text(" ".join([
            "SELECT champions.*",
            "FROM champions, picks, matches",
            f"WHERE champions.name = picks.{filter_side}{db_query_ctype}Champ AND ",
            "picks.address = matches.address AND ",
            "matches.address = :match_add ;",
        ]))

        rows = db.session.execute(stmt, {'match_add': filter_m_addr})
    else:
        rows = []

    return render_template(
        "ui/match_champs.html",

        show_results=show_results,
        rows=rows,

        champ_types=list(champ_types_dict.keys()),
        filter_ctype=db_query_ctype,
        filter_m_addr=filter_m_addr,
        filter_side=filter_side,

        all_sides=['blue', 'red']
    )
