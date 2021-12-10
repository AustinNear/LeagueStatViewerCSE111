from flask import (
    render_template,
    request
)
from sqlalchemy.sql import text

from app import db
from .views import bp_core
from .helpers import int_safe

@bp_core.route('/match/types', endpoint='match_types', methods=['GET'])
def match_types():

    stmt = text("SELECT distinct(type) from matches")
    rows = db.session.execute(stmt).fetchall()

    return render_template(
        'ui/match_types.html',
        
        mt_types=rows
    )


@bp_core.route('/match/longest', endpoint='match_nlongest', methods=['GET'])
def match_nlongest():

    matches_num = max(1, int_safe(request.args.get('n', 5), 5))

    stmt = text("""
        SELECT year, league, type, season, gamelength
        FROM matches
        GROUP BY gamelength
        ORDER BY gamelength DESC
        LIMIT :n;
    """)

    rows = db.session.execute(stmt, {'n': matches_num}).fetchall()

    return render_template(
        'ui/match_nlongest.html',
        rows=rows,
        matches_num=matches_num
    )
