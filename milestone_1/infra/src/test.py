import os
import pystache
from pathlib import Path

from utils.helper import Config

print(Config.get("frontend.bucket.name"))
