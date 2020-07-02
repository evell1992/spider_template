from flask import Blueprint

template_blu = Blueprint('template', __name__, url_prefix="/api/template")
from .views import *
