#!/usr/bin/python3

#implements an http server to receive commands from the user

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import cgi
import json
import configparser
import os

'''Loading config'''
this_file = os.path.dirname(__file__)
config = configparser.RawConfigParser()
config.read(os.path.join(this_file, "config", "main_config.ini"))

if 'HOST_NAME' in config['http']:
    HOST_NAME = config['http']['HOST_NAME']
else:
    HOST_NAME = ""
HOST_PORT = int(config['http']['PORT'])

def MakeHandlerClass(commandqueue, statusqueue):
    class MyHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            commandqueue.put("http:request_status")
            self.send_response(200)
            
            self.send_header("Content-type", "text/json")
            self.end_headers()
            status = statusqueue.get(block=True)
            self.wfile.write(json.dumps(status).encode('utf8'))
            
            path = self.path
            
        def do_POST(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes("Posted!", "utf-8"))
            
            form = cgi.FieldStorage(
                fp = self.rfile,
                headers = self.headers,
                environ = {"REQUEST_METHOD": "POST"}
            )
            
            data = {}
            
            for item in form.list:
                data[item.name] = item.value
            
            if 'command' in data:
                command = data['command']
            commandqueue.put("http:command:{}".format(command))
            
            path = self.path
    return MyHandler

def http_function(commandqueue, statusqueue):
    my_server = HTTPServer((HOST_NAME, HOST_PORT), MakeHandlerClass(commandqueue, statusqueue))
    
    try:
          my_server.serve_forever()
    except KeyboardInterrupt:
        pass

    my_server.server_close()
    print("http server stopped")
