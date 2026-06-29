#!/usr/bin/env python3
"""
GRIT Copilot Portal - Web Server Launcher
Serves the portal from the dist/ directory at http://localhost:8080
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 8080
DIST_DIR = Path(__file__).parent / "dist"

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with no-cache headers and proper error handling"""
    
    def end_headers(self):
        # Disable caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging format
        print(f"[Portal] {self.address_string()} - {format % args}")

def main():
    # Ensure we're in the dist directory
    if not DIST_DIR.exists():
        print(f"❌ Error: Portal dist directory not found at {DIST_DIR}")
        print(f"   Please run 'python generate_portal.py' first to build the portal.")
        return 1
    
    # Check for index.html
    index_file = DIST_DIR / "index.html"
    if not index_file.exists():
        print(f"❌ Error: index.html not found in {DIST_DIR}")
        print(f"   Please run 'python generate_portal.py' to generate the portal.")
        return 1
    
    # Change to dist directory so server serves files from there
    os.chdir(DIST_DIR)
    
    # Create server
    Handler = NoCacheHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("=" * 60)
            print("  🚀 GRIT Copilot Portal Server")
            print("=" * 60)
            print(f"  📂 Serving from: {DIST_DIR}")
            print(f"  🌐 URL:          http://localhost:{PORT}")
            print(f"  🛑 Stop:         Press Ctrl+C")
            print("=" * 60)
            print()
            
            # Open browser automatically
            print("  Opening browser...")
            try:
                webbrowser.open(f"http://localhost:{PORT}")
            except Exception as e:
                print(f"  ⚠️  Could not open browser automatically: {e}")
                print(f"  Please open http://localhost:{PORT} manually")
            
            print()
            print("  Server is running. Waiting for requests...")
            print()
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n  🛑 Shutting down portal server...")
        return 0
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {PORT} is already in use!")
            print(f"   Stop the existing server first:")
            print(f"   Windows: Get-NetTCPConnection -LocalPort {PORT} | Select-Object OwningProcess")
            print(f"   Then: Stop-Process -Id <PID>")
        else:
            print(f"\n❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
