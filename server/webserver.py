from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import time


hostName = "localhost"
serverPort = 8080

counter = 0

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/text")
        self.end_headers()
        self.wfile.write(f'<html><head><title>{counter}</title></head></html>'.encode("utf-8"))
        self.wfile.close()



def start_server():
    # Setup stuff here...
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass    


if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.start()

    while True:
        print("counter: ", counter)
        counter = counter + 1
        time.sleep(3)