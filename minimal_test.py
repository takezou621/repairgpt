#!/usr/bin/env python3
"""
最小限のPythonウェブサーバーテスト
"""
import http.server
import socketserver
import threading
import time

PORT = 8509

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>RepairGPT Test</title></head>
        <body>
            <h1>🔧 RepairGPT Connection Test</h1>
            <p>✅ ウェブサーバーは正常に動作しています</p>
            <p>時刻: """ + str(time.time()) + """</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())

if __name__ == "__main__":
    with socketserver.TCPServer(("localhost", PORT), TestHandler) as httpd:
        print(f"🌐 Test server running at http://localhost:{PORT}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")