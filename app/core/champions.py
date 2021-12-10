import math
import urllib.parse

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
)
from flask_wtf import FlaskForm
from wtforms.fields import StringField, IntegerField, HiddenField
from wtforms import validators as vl
from sqlalchemy.sql import text

from app import db
from .views import bp_core
from .constants import AlertType
from .helpers import champ_types_dict, int_safe

@bp_core.route('/champ/winvslosses', endpoint='champ_wls', methods=['GET'])
def champ_wls():

    filter_champ_name = request.args.get("champ_name", '').strip()

    filter_ctype = request.args.get("ctype", '')
    db_query_ctype = champ_types_dict.get(filter_ctype, 'Top')

    show_results = db_query_ctype and filter_champ_name

    stats = [0, 0]

    if show_results:
        stmt = text(
            "SELECT (rwins + bwins) as Wins, (blosses + rlosses) as Losses FROM "
            "(SELECT count(matches.rresult) as rwins from picks, matches "
            "    ON (picks.redteamtag = matches.redteamtag) WHERE matches.rresult = '1' and "
            f"    picks.red{db_query_ctype}Champ = :plr_name ), "
            "(SELECT count(matches.bresult) as bwins from picks, matches "
            "    ON (picks.blueteamtag = matches.blueteamtag) WHERE matches.bresult = '1' and "
            f"    picks.blue{db_query_ctype}Champ = :plr_name ), "
            "(SELECT count(matches.rresult) as rlosses from picks, matches "
            "    ON  (picks.redteamtag = matches.redteamtag)  WHERE matches.rresult = '0' and "
            f"    picks.red{db_query_ctype}Champ = :plr_name ), "
            "(SELECT count(matches.bresult) as blosses from picks, matches "
            "    ON (picks.blueteamtag = matches.blueteamtag) WHERE matches.bresult = '0' and "
            f"    picks.blue{db_query_ctype}Champ = :plr_name ) "
        )

        stats = db.session.execute(stmt, {'plr_name': filter_champ_name}).fetchone()

    return render_template(
        'ui/champ_wls.html',

        filter_champ_name=filter_champ_name,
        filter_ctype=db_query_ctype,

        champ_types=list(champ_types_dict.keys()),
        show_results=show_results,

        stats=stats
    )


@bp_core.route('/champ/list', endpoint='champs_list', methods=['GET'])
def champs_list():

    filter_champ_id = request.args.get("f_champ_id", '').strip()
    filter_name = request.args.get("f_name", '').strip()
    filter_cclass = request.args.get("f_cclass", '').strip()
    filter_difficulty = request.args.get("f_difficulty", '').strip()
    filter_style = request.args.get("f_style", '').strip()
    filter_dtype = request.args.get("f_dtype", '').strip()
    filter_damage = request.args.get("f_damage", '').strip()
    filter_stdr = request.args.get("f_stdr", '').strip()
    filter_cctrl = request.args.get("f_cctrl", '').strip()
    filter_mobl = request.args.get("f_mobl", '').strip()
    filter_func = request.args.get("f_func", '').strip()

    page_size = 40;
    page_num = max(int_safe(request.args.get('page', 1) or 1, 1), 1)

    where_clauses = " ".join([
        "AND Id = :champ_id" if filter_champ_id != '' else '', 
        "AND Name = :name" if filter_name != '' else '', 
        "AND Class = :cclass" if filter_cclass != '' else '', 
        "AND style = :style" if filter_style != '' else '', 
        "AND difficulty = :difficulty" if filter_difficulty != '' else '', 
        "AND DamageType = :dtype" if filter_dtype != '' else '', 
        "AND Damage = :damage" if filter_damage != '' else '', 
        "AND Sturdiness = :stdr" if filter_stdr != '' else '', 
        "AND \"Crowd-Control\" = :cctrl" if filter_cctrl != '' else '', 
        "AND Mobility = :mobl" if filter_mobl != '' else '', 
        "AND Functionality = :func" if filter_func != '' else '', 
    ])

    where_clause_params = {
        'champ_id': filter_champ_id,
        'name': filter_name,
        'cclass': filter_cclass,
        'style': filter_style,
        'difficulty': filter_difficulty,
        'dtype': filter_dtype,
        'damage': filter_damage,
        'stdr': filter_stdr,
        'cctrl': filter_cctrl,
        'mobl': filter_mobl,
        'func': filter_func,
    }

    stmt = text(" ".join([
        "SELECT * from champions WHERE 1",
        where_clauses,
        "ORDER BY Id",
        f"LIMIT {(page_num - 1) * page_size}, {page_size}"
    ]))

    rows = db.session.execute(stmt, where_clause_params).fetchall()

    count_stmt = text(" ".join([
        "SELECT count(Id) FROM champions WHERE 1",
        where_clauses
    ]))
    count_result = db.session.execute(count_stmt, where_clause_params).fetchone()
    total_pages = math.ceil(count_result[0] / page_size)

    return render_template(
        "ui/champs_list.html",

        rows=rows,

        filter_champ_id=filter_champ_id,
        filter_name=filter_name,
        filter_cclass=filter_cclass,
        filter_difficulty=filter_difficulty,
        filter_style=filter_style,
        filter_dtype=filter_dtype,
        filter_damage=filter_damage,
        filter_stdr=filter_stdr,
        filter_cctrl=filter_cctrl,
        filter_mobl=filter_mobl,
        filter_func=filter_func,

        current_page=page_num,
        total_pages=total_pages,
        render_page_start=max(1, page_num - 2),
        render_page_end=min(total_pages, page_num + 2),

        filter_query_str='?' + urllib.parse.urlencode(where_clause_params)
    )


class AddChampionForm(FlaskForm):
    champ_id   = StringField("", validators=[vl.InputRequired()])
    name       = StringField("", validators=[vl.InputRequired()])
    cclass     = StringField("", validators=[vl.InputRequired()])
    style      = IntegerField("", validators=[vl.InputRequired()])
    difficulty = IntegerField("", validators=[vl.InputRequired()])
    dtype      = StringField("", validators=[vl.InputRequired()])
    damage     = IntegerField("", validators=[vl.InputRequired()])
    stdr       = IntegerField("", validators=[vl.InputRequired()])
    cctrl      = IntegerField("", validators=[vl.InputRequired()])
    mobl       = IntegerField("", validators=[vl.InputRequired()])
    func       = IntegerField("", validators=[vl.InputRequired()])

@bp_core.route('/champ/add', endpoint='champ_add', methods=['GET', 'POST'])
def champ_add():
    form = AddChampionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            
            # Add the champions
            stmt = text("""
                INSERT INTO champions VALUES
                (
                    :champ_id, :name, :cclass, 
                    :difficulty, :style,
                    :dtype, :damage,
                    :stdr, :cctrl,
                    :mobl, :func
                )
            """);

            db.session.execute(stmt, {
                'champ_id':     form.champ_id.data,
                'name':         form.name.data,
                'cclass':       form.cclass.data,
                'difficulty':   form.difficulty.data,
                'style':        form.style.data,
                'dtype':        form.dtype.data,
                'damage':       form.damage.data,
                'stdr':         form.stdr.data,
                'cctrl':        form.cctrl.data,
                'mobl':         form.mobl.data,
                'func':         form.func.data,
            })

            flash("Champion added successfully", AlertType.Success)
        else:
            flash("Invalid form data", AlertType.Error)

        return redirect(url_for('core.champ_add'))

    return render_template(
        'ui/champ_add.html',

        form=form
    )


class DeleteChampForm(FlaskForm):
    champ_id   = HiddenField("", validators=[vl.InputRequired()])

@bp_core.route('/champ/update/<champ_id>', endpoint='champ_update', methods=['GET', 'POST'])
def champ_update(champ_id):
    champion = db.session.execute("SELECT * FROM champions WHERE Id = :champ_id ; ", {
        'champ_id': champ_id
    }).fetchone()

    if champion is None:
        abort(404)

    form = AddChampionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            
            # Update the champion
            stmt = text("""
                UPDATE champions
                SET 
                    Id              = :champ_id ,
                    Name            = :name ,
                    Class           = :cclass ,
                    Style           = :difficulty ,
                    Difficulty      = :style ,
                    DamageType      = :dtype ,
                    Damage          = :damage ,
                    Sturdiness      = :stdr ,
                    "Crowd-Control" = :cctrl ,
                    Mobility        = :mobl ,
                    Functionality   = :func

                WHERE Id = :orignal_id ;
            """);

            db.session.execute(stmt, {
                'orignal_id':     champ_id,

                'champ_id':     form.champ_id.data,
                'name':         form.name.data,
                'cclass':       form.cclass.data,
                'difficulty':   form.difficulty.data,
                'style':        form.style.data,
                'dtype':        form.dtype.data,
                'damage':       form.damage.data,
                'stdr':         form.stdr.data,
                'cctrl':        form.cctrl.data,
                'mobl':         form.mobl.data,
                'func':         form.func.data,
            })

            flash("Champion updated successfully", AlertType.Success)
            return redirect(url_for('core.champs_list') + f"?f_champ_id={form.champ_id.data}")
        else:
            flash("Invalid form data", AlertType.Error)
            return redirect(url_for('core.champ_update', champ_id=champ_id))

    form.champ_id.data   = champion[0]
    form.name.data       = champion[1]
    form.cclass.data     = champion[2]
    form.style.data      = champion[3]
    form.difficulty.data = champion[4]
    form.dtype.data      = champion[5]
    form.damage.data     = champion[6]
    form.stdr.data       = champion[7]
    form.cctrl.data      = champion[8]
    form.mobl.data       = champion[9]
    form.func.data       = champion[10]

    return render_template(
        "ui/champ_update.html",

        form=form,
        delete_form=DeleteChampForm(),
        champ_id=champ_id,
        champ_name=form.name.data
    )

@bp_core.route('/champ/delete', endpoint='champ_delete', methods=['POST'])
def champ_delete():
    form = DeleteChampForm()

    if form.validate_on_submit():

        stmt = text("DELETE FROM champions WHERE champions.Id = :champ_id ;");

        db.session.execute(stmt, {
            'champ_id': form.champ_id.data
        })

        flash("Champion deleted successfully", AlertType.Success)
    else:
        flash("Invalid form data", AlertType.Error)

    return redirect(url_for('core.champs_list'))
