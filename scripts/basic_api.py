#!/usr/bin/env python
"""
Basic API Server for ADE Platform

This script runs a minimal HTTP server to test basic API functionality.
"""

import http.server
import socketserver
import json
import logging
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Handler for HTTP requests
class AdeApiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Health check endpoint
        if path == "/health":
            self._handle_health_check()
            
        # Get prompt status endpoint
        elif path.startswith("/api/prompt/"):
            task_id = path.split("/")[-1]
            self._handle_prompt_status(task_id)
            
        else:
            # Return 404 for all other paths
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Process prompt endpoint
        if path == "/api/prompt":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                self._handle_process_prompt(request_data)
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                
        else:
            # Return 404 for all other paths
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_OPTIONS(self):
        # Handle preflight CORS requests
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _handle_health_check(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        response = {
            "status": "ok",
            "message": "ADE Basic API Server is running",
            "version": "1.0.0"
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_process_prompt(self, request_data):
        prompt = request_data.get("prompt", "")
        logger.info(f"Received prompt: {prompt[:50]}...")
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        response = {
            "task_id": "task_123",
            "status": "accepted",
            "message": f"Processing prompt: {prompt[:50]}..."
        }
        
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_prompt_status(self, task_id):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        response = {
            "task_id": task_id,
            "status": "completed",
            "result": {
                "code": "console.log('Hello from ADE platform');"
            }
        }
        
        self.wfile.write(json.dumps(response).encode())

def main():
    PORT = 8000
    Handler = AdeApiHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logger.info(f"Starting basic API server at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            httpd.server_close()
            logger.info("Server closed")

if __name__ == "__main__":
    main()
