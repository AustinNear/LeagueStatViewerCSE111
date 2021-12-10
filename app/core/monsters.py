from flask import (
    render_template,
    request
)
from sqlalchemy.sql import text

from app import db
from .views import bp_core

@bp_core.route('/monster/types', endpoint='monster_types', methods=['GET'])
def monster_types():

    stmt = text("SELECT distinct(type) from monsters")
    rows = db.session.execute(stmt).fetchall()

    return render_template(
        'ui/monster_types.html',
        
        mn_types=rows
    )



@bp_core.route('/monster/kills', endpoint='monster_kills', methods=['GET'])
def monster_kills():

    mn_types_stmt = text("SELECT distinct(type) from monsters WHERE type != '' ORDER BY type")
    mn_types_db = db.session.execute(mn_types_stmt).fetchall()
    mn_types = list(map(lambda row: row[0], mn_types_db))

    side_types_stmt = text("SELECT distinct(team) from monsters WHERE team != '' ORDER BY team")
    side_types_db = db.session.execute(side_types_stmt).fetchall()
    side_types = list(map(lambda row: row[0], side_types_db))

    filter_selected_type = request.args.get("monster_type", mn_types[0] if len(mn_types) > 0 else '')

    filter_selected_bside = request.args.get("bside_type", side_types[0] if len(side_types) > 0 else '')
    filter_selected_rside = request.args.get("rside_type", side_types[0] if len(side_types) > 0 else '')

    stmt = text("""
        SELECT 'Blue', count(*) FROM monsters WHERE team = :bside_type and type = :monster_type
        UNION
        SELECT 'Red', count(*) FROM monsters WHERE team = :rside_type and type = :monster_type ;
    """)

    stats = db.session.execute(stmt, {
        'bside_type': filter_selected_bside,
        'rside_type': filter_selected_rside,
        'monster_type': filter_selected_type,
    }).fetchall()

    return render_template(
        "ui/monster_kills.html",

        mn_types=mn_types,
        side_types=side_types,

        filter_selected_type=filter_selected_type,
        filter_selected_bside=filter_selected_bside,
        filter_selected_rside=filter_selected_rside,

        blue_kills=stats[0][1],
        red_kills=stats[1][1],
    )
