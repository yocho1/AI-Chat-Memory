from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"📥 GET request: {self.path}")
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if self.path == '/':
            response = {'message': 'Simple server working!'}
        elif self.path == '/api/ping':
            response = {'message': 'pong'}
        elif self.path == '/api/health':
            response = {'status': 'healthy'}
        else:
            response = {'error': 'Not found', 'path': self.path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        print(f"📥 POST request: {self.path}")
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if self.path == '/api/chat':
            try:
                data = json.loads(post_data.decode())
                user_message = data.get('message', '')
                response = {
                    'response': f'Simple server response to: {user_message}',
                    'session_id': 'simple-session',
                    'demo': True
                }
            except:
                response = {'error': 'Invalid JSON'}
        else:
            response = {'error': 'Not found', 'path': self.path}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        print(f"📥 OPTIONS request: {self.path}")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"🚀 Starting simple HTTP server on port {port}")
    server.serve_forever()