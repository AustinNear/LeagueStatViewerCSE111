from flask import (
    render_template,
)
from sqlalchemy.sql import text

from app import db
from .views import bp_core

@bp_core.route('/structure/types', endpoint='structure_types', methods=['GET'])
def structure_types():

    stmt = text("SELECT distinct(type) from structures")
    rows = db.session.execute(stmt).fetchall()

    return render_template(
        'ui/structure_types.html',
        
        st_types=rows
    )
