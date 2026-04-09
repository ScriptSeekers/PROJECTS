import http.server
import socketserver
import sys
import os

def run_server(port=8000):
    """Run a simple HTTP server on the specified port."""
    
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create handler
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Set up server
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"🍾 Bottle Hunt Server")
        print(f"📡 Server running at http://localhost:{port}/")
        print(f"🎮 Open your browser and go to http://localhost:{port}/")
        print(f"⏹️  Press Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped. Thanks for playing!")
            sys.exit(0)

if __name__ == "__main__":
    # Get port from command line argument or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
