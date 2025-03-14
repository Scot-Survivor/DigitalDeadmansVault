import glob
import colorama

from os.path import basename, dirname, isfile, join

colorama.init()
modules = glob.glob(join(dirname(__file__), "*//*.py"), recursive=True)
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
