import os
import json
from http.server import SimpleHTTPRequestHandler
from .graph_data_handler import GraphDataHandler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DIRECTORY = os.path.join(SCRIPT_DIR, "public")


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, graph_data_handler: GraphDataHandler, **kwargs):
        self._graph_data_handler = graph_data_handler
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        self.path = "/"

    def _api_data_route_action(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        response = json.dumps(self._graph_data_handler.handle())
        return self.wfile.write(response.encode("utf-8"))

    def _home_route_action(self):
        if self.path != "/" and not os.path.exists(os.path.join(DIRECTORY, self.path.strip("/"))):
            self.path = "/index.html"

        return super().do_GET()

    def do_GET(self):  # noqa: N802
        if self.path == "/api/data":
            return self._api_data_route_action()

        return self._home_route_action()
