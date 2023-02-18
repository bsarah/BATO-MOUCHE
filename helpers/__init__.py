print("--- Import helpers ---")

from . import scrapping
from . import visualize

#to assure that reload(helpers) reloads everything in the folder.
from importlib import reload
reload(scrapping)
reload(visualize)

#to not have to import each file separetly.
from .scrapping import *
from .visualize import *