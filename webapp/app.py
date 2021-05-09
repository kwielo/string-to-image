import web
import logging, requests
from urllib.parse import parse_qs
from jsonpath_ng import parse
from requests import RequestException
from webapp.draw_text import DrawText
from webapp.validation import check_json_path, check_url, check_font
from webapp.utils import *

from webapp.exceptions import QueryParameterError

logger = logging.getLogger(__name__)

urls = (
    '/api/v1/string-to-image',  'api_v1_string_to_image',
    '/api/v1/json-to-image', 'api_v1_json_to_image',
)
app = web.application(urls, globals())


def generate_and_return_image(text, font_name, font_size):
    filepath = get_filepath(get_filename([text, font_name, font_size]))
    image_file = get_existing_file(filepath)
    if image_file is not None:
        return image_file

    image_filepath = DrawText(
        text, font_name, font_size
    ).save_image(filepath)

    return load_file(image_filepath)


class api_v1_string_to_image:
    def GET(self):
        pq = parse_qs(web.ctx.query[1:])
        text = get_query_param(pq, "text", "add ?text=custom_text")
        font_name = get_query_param(pq, "font_name", DrawText.DEFAULT_FONT_NAME)
        font_size = int(get_query_param(pq, "font_size", DrawText.DEFAULT_FONT_SIZE))

        try:
            check_font(font_name)
        except QueryParameterError as err:
            text = f"Wrong parameter '{err.expression}': {err.message}"

        web.header('Content-type', 'image/png')
        return generate_and_return_image(text, font_name, font_size)


class api_v1_json_to_image:
    def GET(self):
        pq = parse_qs(web.ctx.query[1:])
        json_url = get_query_param(pq, "json_url", "")
        json_path = get_query_param(pq, "json_path", "")
        font_name = get_query_param(pq, "font_name", DrawText.DEFAULT_FONT_NAME)
        font_size = int(get_query_param(pq, "font_size", DrawText.DEFAULT_FONT_SIZE))

        try:
            check_url(json_url)
            check_json_path(json_path)
            check_font(font_name)
        except QueryParameterError as err:
            text = f"Wrong parameter '{err.expression}': {err.message}"

        try:
            text = get_json_value(json_url, json_path)
        except RequestException:
            text = f"'json_url' has invalid or wrong url"

        web.header('Content-type', 'image/png')
        return generate_and_return_image(text, font_name, font_size)


if __name__ == "__main__":
    app.run()
