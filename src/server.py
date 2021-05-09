from http.server import BaseHTTPRequestHandler, HTTPServer
import logging, glob, requests, hashlib, os
from urllib.parse import urlparse, parse_qs, unquote
from jsonpath_ng import jsonpath, parse
from requests import RequestException
from src.draw_text import DrawText

from src.exceptions import QueryParameterError

PORT = 8000


class Handler(BaseHTTPRequestHandler):
    map_get_requests = {
        '/api/v1/string-to-image': '_api_v1_string_to_image',
        '/api/v1/json-to-image': '_api_v1_json_to_image',
    }

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self.parsed_path = urlparse(self.path)
        if self.parsed_path.path in self.map_get_requests.keys():
            getattr(self, self.map_get_requests[self.parsed_path.path])()
        else:
            self._set_default_response()
            self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def _api_v1_string_to_image(self):
        self.parsed_query = parse_qs(self.parsed_path.query)
        qp_text = self._get_query_param('text', "add ?text=custom_text")
        qp_font_name = self._get_query_param('font_name', DrawText.DEFAULT_FONT_NAME)
        qp_font_size = int(self._get_query_param('font_size', DrawText.DEFAULT_FONT_SIZE))

        try:
            self._check_font(qp_font_name)
        except QueryParameterError as err:
            qp_text = f"Wrong parameter '{err.expression}': {err.message}"

        self._send_image(qp_text, qp_font_name, qp_font_size)

    def _api_v1_json_to_image(self):

        self.parsed_query = parse_qs(self.parsed_path.query)
        qp_json_source = self._get_query_param('json_source', '')
        qp_json_path = self._get_query_param('json_path', "add ?json_path=info.version")
        qp_font_name = self._get_query_param('font_name', DrawText.DEFAULT_FONT_NAME)
        qp_font_size = int(self._get_query_param('font_size', DrawText.DEFAULT_FONT_SIZE))

        try:
            self._check_url(qp_json_source)
            self._check_json_path(qp_json_path)
            self._check_font(qp_font_name)
        except QueryParameterError as err:
            text = f"Wrong parameter '{err.expression}': {err.message}"

        try:
            json_obj = requests.get(qp_json_source).json()
            jsonpath_expr = parse(qp_json_path)
            text = ", ".join([match.value for match in jsonpath_expr.find(json_obj)])
        except RequestException:
            text = f"'json_source' has invalid or wrong url"

        filepath = self._get_filepath(self._get_filename([text, qp_font_name, qp_font_size]))
        if self._get_existing_file(filepath):
            self._send_image_file(filepath)
        else:
            self._send_image(text, qp_font_name, qp_font_size, filepath)

    def _send_image(self, text, font_name, font_size, filepath=None):
        img_filename = DrawText(text, font_name, font_size).save_image(filepath)
        self._send_image_file(img_filename)

    def _send_image_file(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        self.wfile.write(self._load(filename))

    def _get_existing_file(self, filepath):
        return os.path.exists(filepath)

    def _get_filepath(self, filename):
        return f"tmp/{filename}"

    def _get_filename(self, params):
        return f"{self._get_hash_key(params)}.png"

    def _get_hash_key(self, key_items):
        hash_obj = hashlib.sha256("|".join(map(lambda s: str(s), key_items)).encode('utf-8'))
        return hash_obj.hexdigest()

    def _get_query_param(self, name, default=''):
        q = self.parsed_query
        if name in q and len(q[name]):
            return unquote(q[name].pop()) if len(q[name]) == 1 else unquote(q[name])
        else:
            return default

    @staticmethod
    def _check_url(url):
        import validators
        if not validators.url(url):
            raise QueryParameterError("json_source", "Invalid url")

    @staticmethod
    def _check_json_path(path):
        pass

    @staticmethod
    def _check_font(font_name):
        dirpath = "resources/"
        if f"{dirpath}{font_name}.ttf" not in glob.glob(f"{dirpath}*.ttf"):
            raise QueryParameterError("font_name", f"font {font_name} doesn't exist")

    def _load(self, filename):
        with open(filename, 'rb') as file:
            return file.read()

    def _set_default_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=Handler, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        logging.info(f"Listening on: {httpd.server_name}:{httpd.server_port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
