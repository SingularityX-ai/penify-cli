import json
import webbrowser
import http.server
import socketserver
import urllib.parse
import random
from threading import Thread
from pathlib import Path
from ..api_client import APIClient

def save_credentials(api_key):
    """Save the token and API keys in the .penify file in the user's home
    directory.

    This function creates a dictionary containing the provided API key and
    attempts to write it to a file named '.penify' located in the user's
    home directory. If the operation is successful, it returns True. If
    there is an error during the file writing process, it catches the
    exception, prints an error message, and returns False.

    Args:
        api_key (str): The API key to be saved.

    Returns:
        bool: True if the credentials were saved successfully, False otherwise.
    """
    home_dir = Path.home()
    penify_file = home_dir / '.penify'

    credentials = {
        'api_keys': api_key
    }

    try:
        with open(penify_file, 'w') as f:
            json.dump(credentials, f)
        return True
    except Exception as e:
        print(f"Error saving credentials: {str(e)}")
        return False

def login(api_url, dashboard_url):
    """Open the login page in a web browser and listen for the redirect URL to
    capture the token.

    This function generates a unique redirect URL and opens the login page
    in the user's default web browser. It listens for a redirect from the
    authentication service, captures the token from the URL, and attempts to
    fetch the API key using the provided token. If successful, it saves the
    API key for future use. The user is informed of the login status through
    printed messages and an HTML response.

    Args:
        api_url (str): The URL of the API to fetch the API key from.
        dashboard_url (str): The URL of the dashboard to redirect to after login.
    """
    redirect_port = random.randint(30000, 50000)
    redirect_url = f"http://localhost:{redirect_port}/callback"
    
    full_login_url = f"{dashboard_url}?redirectUri={urllib.parse.quote(redirect_url)}"
    
    print(f"Opening login page in your default web browser: {full_login_url}")
    webbrowser.open(full_login_url)
    
    class TokenHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            """Handle GET requests for the login process.

            This method processes incoming GET requests by extracting the token from
            the query parameters. If a valid token is provided, it sends a success
            response with an HTML page that informs the user of a successful login
            and redirects them to the Penify dashboard after 5 seconds. It also
            attempts to fetch and save API keys using the provided token. If the
            token is missing or invalid, it sends a failure response with an
            appropriate message.
            """

            query = urllib.parse.urlparse(self.path).query
            query_components = urllib.parse.parse_qs(query)
            token = query_components.get("token", [None])[0]
            
            if token:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                response = """
                <html>
                <head>
                    <script>
                        setTimeout(function() {
                            window.location.href = 'https://dashboard.penify.dev';
                        }, 5000);
                    </script>
                </head>
                <body>
                    <h1>Login Successful!</h1>
                    <p>You will be redirected to the Penify dashboard in 5 seconds. You can also close this window and return to the CLI.</p>
                </body>
                </html>
                """
                self.wfile.write(response.encode())
                
                print(f"\nLogin successful! Fetching API keys...")
                api_key = APIClient(api_url, None, token).get_api_key()
                if api_key:
                    save_credentials(api_key)
                    print("API keys fetched and saved successfully.")
                    print("You'll be redirected to the Penify dashboard. You can continue using the CLI.")
                else:
                    print("Failed to fetch API keys.")
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                response = """
                <html>
                <body>
                <h1>Login Failed</h1>
                <p>Please try again.</p>
                </body>
                </html>
                """
                self.wfile.write(response.encode())
                print("\nLogin failed. Please try again.")
            
            # Schedule the server shutdown
            thread = Thread(target=self.server.shutdown)
            thread.daemon = True
            thread.start()

        def log_message(self, format, *args):
            # Suppress log messages
            return
    
    with socketserver.TCPServer(("", redirect_port), TokenHandler) as httpd:
        print(f"Listening on port {redirect_port} for the redirect...")
        httpd.serve_forever()
    
    print("Login process completed. You can now use other commands with your API token.")
