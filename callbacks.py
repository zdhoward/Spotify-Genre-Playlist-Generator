import random
import string

import cherrypy

# CONFIG = {'/callback':{'server.socket_host': '127.0.0.1','server.socket_port': 9000,'log.screen': False}}
cherrypy.config.update({"log.screen": False})


class CallbackHandler(object):
    response = None

    @cherrypy.expose
    def index(self):
        request = cherrypy.serving.request
        self.response = cherrypy.url(qs=request.query_string)
        cherrypy.engine.exit()


def await_callback():
    handle = CallbackHandler()
    cherrypy.quickstart(handle, "/callback", config={"/": {"log.screen": False}})
    return handle.response


if __name__ == "__main__":
    answer = await_callback()
    print(answer)
