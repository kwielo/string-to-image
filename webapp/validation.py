from glob import glob
from exceptions import QueryParameterError


def check_font(font_name):
    dirpath = "resources/"
    if f"{dirpath}{font_name}.ttf" not in glob(f"{dirpath}*.ttf"):
        raise QueryParameterError("font_name", f"font {font_name} doesn't exist")


def check_url(url):
    import validators
    if not validators.url(url):
        raise QueryParameterError("json_source", "Invalid url")


def check_json_path(path):
    pass