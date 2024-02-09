from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class NotificationHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        print("Received Notification:")
        print(json.dumps(data, indent=2))

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Notification Received')

def run_server(port=5050):
    server_address = ('', port)
    httpd = HTTPServer(server_address, NotificationHandler)
    print(f"Listening on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
