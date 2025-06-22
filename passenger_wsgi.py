import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app as application  # если у вас app = Flask(__name__)

