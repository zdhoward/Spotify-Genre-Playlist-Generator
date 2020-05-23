import cherrypy
import platform

os_type = platform.system()

if os_type == "Linux":
    binary_location = "/usr/bin/chromedriver"
elif os_type == "Windows":
    binary_location = "C:\\Windows\\chromedriver.exe"
else:
    print("Chromedriver for Mac OS not configured")
    exit(1)

# CONFIG = {'/callback':{'server.socket_host': '127.0.0.1','server.socket_port': 9000,'log.screen': False}}
cherrypy.config.update({"log.screen": False})


def wait_for_http_callback(_port=9000, _host="127.0.0.1"):
    import cherrypy

    if _host == "localhost":
        _host = "127.0.0.1"

    cherrypy.config.update(
        {"server.socket_host": _host, "server.socket_port": _port, "log.screen": False}
    )

    class CallbackHandler(object):
        response = None

        @cherrypy.expose
        def index(self, code=None):
            request = cherrypy.serving.request
            self.response = cherrypy.url(qs=request.query_string)
            cherrypy.engine.exit()

    handle = CallbackHandler()
    cherrypy.quickstart(handle, "/callback", config={"/": {"log.screen": False}})
    return handle.response


def visit_url(_url):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = binary_location

    driver = webdriver.Chrome(executable_path=binary_location)
    driver.get(_url)
    driver.implicitly_wait(3)
    return driver.current_url


if __name__ == "__main__":
    answer = await_callback()
    print(answer)
