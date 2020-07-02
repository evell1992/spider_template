from flask import Blueprint

index_blu = Blueprint('', __name__, url_prefix="")
from .views import *
