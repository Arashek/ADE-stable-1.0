import http.server
import socketserver
import os

# Change to the static directory
os.chdir('static')

# Create the server
PORT = 3001
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever() 