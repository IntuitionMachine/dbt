import shutil
import os
import webbrowser

from dbt.include.global_project import DOCS_INDEX_FILE_PATH
from dbt.compat import SimpleHTTPRequestHandler, TCPServer
from dbt.logger import GLOBAL_LOGGER as logger

from dbt.task.base import ProjectOnlyTask


class ServeTask(ProjectOnlyTask):
    def run(self):
        os.chdir(self.config.target_path)

        port = self.args.port

        shutil.copyfile(DOCS_INDEX_FILE_PATH, 'index.html')

        logger.info("Serving docs at 0.0.0.0:{}".format(port))
        logger.info(
            "To access from your browser, navigate to http://localhost:{}."
            .format(port)
        )
        logger.info("Press Ctrl+C to exit.\n\n")

        httpd = TCPServer(
            ('0.0.0.0', port),
            SimpleHTTPRequestHandler
        )

        try:
            webbrowser.open_new_tab('http://127.0.0.1:{}'.format(port))
        except webbrowser.Error as e:
            pass

        try:
            httpd.serve_forever()  # blocks
        finally:
            httpd.shutdown()
            httpd.server_close()

        return None
