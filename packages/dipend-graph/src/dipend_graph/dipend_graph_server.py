import os
import signal
import sys
import threading
from time import sleep
from http.server import ThreadingHTTPServer
from typing import Optional, Any
from .graph_data_handler import GraphDataHandler
from .request_handler import RequestHandler


class DipendGraphServer:
    def __init__(
        self,
        dependency_container: Any,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        env_host, env_port = self._get_envs()
        self._host = host if host else env_host
        self._port = port if port else env_port
        self._graph_data_handler = GraphDataHandler(dependency_container)
        self._httpd = ThreadingHTTPServer((self._host, self._port), lambda *args, **kwargs: RequestHandler(*args, graph_data_handler=self._graph_data_handler, **kwargs))
        self._server_thread: threading.Thread = None

    def _get_envs(self):
        host = os.getenv("SERVER_HOST", "127.0.0.1")
        port = int(os.getenv("SERVER_PORT", "4321"))

        return host, port

    def _graceful_shutdown(self, signum, frame):
        print("\nShutting down the server gracefully...")
        self._httpd.socket.close()
        self._httpd.server_close()
        self._httpd.shutdown()
        sys.exit(0)

    def start(self):
        print(f"Serving the dipend Graph at http://{self._host}:{self._port}")

        signal.signal(signal.SIGINT, self._graceful_shutdown)

        self._server_thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._server_thread.start()

    def hang(self):
        while True:
            try:
                sleep(1)
            except KeyboardInterrupt:
                self._graceful_shutdown()
