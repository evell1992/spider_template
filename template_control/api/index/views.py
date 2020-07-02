from flask import render_template

from template_control.api.index import index_blu


@index_blu.route("/", methods=["GET"])
def admin():
    return render_template('index.html')