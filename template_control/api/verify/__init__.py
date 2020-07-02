from flask import Blueprint

verify_blu = Blueprint('verify', __name__, url_prefix="/api/verify")
from .views import *
