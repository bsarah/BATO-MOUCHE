print("--- Import helpers ---")

import os
os.environ['USE_PYGEOS'] = '0'

from . import scrapping
from . import visualize
from . import scrapping_big

#to assure that reload(helpers) reloads everything in the folder.
from importlib import reload
reload(scrapping)
reload(visualize)
reload(scrapping_big)

#to not have to import each file separetly.
from .scrapping import *
from .visualize import *
from .scrapping_big import *