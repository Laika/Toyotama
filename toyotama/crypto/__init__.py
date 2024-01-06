from logging import getLogger

from toyotama.crypto.aes import *
from toyotama.crypto.classical_cipher import *
from toyotama.crypto.const import *
from toyotama.crypto.curve import *
from toyotama.crypto.hash import *
from toyotama.crypto.rng import *
from toyotama.crypto.rsa import *
from toyotama.crypto.util import *

try:
    from sage.all import *

    from toyotama.crypto.lattice import *
    from toyotama.crypto.polynomial import *
except ImportError:
    logger = getLogger(__name__)
    logger.warning("SageMath is not installed. Some functions may not work.")
