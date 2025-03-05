import json
import random
import webbrowser
import http.server
import socketserver
import pkg_resources
from pathlib import Path
from threading import Thread

def save_llm_config(model, api_base, api_key):
    """Save LLM configuration settings in the .penify file.

    This function saves the specified model, API base, and API key into a
    configuration file located in the user's home directory. If the
    configuration file already exists, it attempts to load the existing
    settings. The function updates or adds the LLM configuration with the
    provided parameters and writes the updated configuration back to the
    file. If any errors occur during the file operations, they are caught
    and logged.

    Args:
        model (str): The name of the model to be saved.
        api_base (str): The base URL for the API.
        api_key (str): The API key for authentication.

    Returns:
        bool: True if the configuration was saved successfully, False otherwise.
    """
    home_dir = Path.home()
    penify_file = home_dir / '.penify'
    
    config = {}
    if penify_file.exists():
        try:
            with open(penify_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # Update or add LLM configuration
    config['llm'] = {
        'model': model,
        'api_base': api_base,
        'api_key': api_key
    }
    
    try:
        with open(penify_file, 'w') as f:
            json.dump(config, f)
        print(f"LLM configuration saved to {penify_file}")
        return True
    except Exception as e:
        print(f"Error saving LLM configuration: {str(e)}")
        return False

def save_jira_config(url, username, api_token):
    """Save JIRA configuration settings in the .penify file.

    This function saves the provided JIRA configuration settings, including
    the URL, username, and API token, into a file named '.penify' located in
    the user's home directory. If the file already exists, it attempts to
    load the existing configuration and updates it with the new JIRA
    settings. The configuration is stored in JSON format.

    Args:
        url (str): The URL of the JIRA instance.
        username (str): The username for JIRA authentication.
        api_token (str): The API token for JIRA authentication.

    Returns:
        bool: True if the configuration was saved successfully, False otherwise.
    """
    home_dir = Path.home()
    penify_file = home_dir / '.penify'
    
    config = {}
    if penify_file.exists():
        try:
            with open(penify_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # Update or add JIRA configuration
    config['jira'] = {
        'url': url,
        'username': username,
        'api_token': api_token
    }
    
    try:
        with open(penify_file, 'w') as f:
            json.dump(config, f)
        print(f"JIRA configuration saved to {penify_file}")
        return True
    except Exception as e:
        print(f"Error saving JIRA configuration: {str(e)}")
        return False

def get_llm_config():
    """Retrieve the LLM configuration from the .penify file.

    This function checks for the existence of a configuration file named
    '.penify' in the user's home directory. If the file exists, it attempts
    to read and parse the JSON content of the file. The function returns the
    'llm' section of the configuration if present, or an empty dictionary if
    the section is not found or if any error occurs during file reading or
    JSON decoding.

    Returns:
        dict: The LLM configuration as a dictionary, or an empty dictionary
        if the configuration file does not exist or an error occurs.
    """
    config_file = Path.home() / '.penify'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('llm', {})
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading .penify config file: {str(e)}")
    
    return {}

def get_jira_config():
    """Retrieve JIRA configuration from the .penify file.

    This function checks for the existence of a configuration file named
    '.penify' in the user's home directory. If the file exists, it attempts
    to read the file and parse it as JSON. The function specifically looks
    for the 'jira' key in the parsed configuration and returns its value. If
    the file does not exist or if there is an error reading or parsing the
    file, an empty dictionary is returned.

    Returns:
        dict: The JIRA configuration settings, or an empty dictionary if
        the configuration file does not exist or cannot be read.
    """
    config_file = Path.home() / '.penify'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('jira', {})
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading .penify config file: {str(e)}")
    
    return {}

def config_llm_web():
    """Open a web browser interface for configuring LLM settings.

    This function starts a simple HTTP server that serves a web page for
    configuring settings related to a language model (LLM). It generates a
    random port number for the server and opens the configuration page in
    the user's default web browser. The server handles GET requests to serve
    the configuration HTML template and POST requests to save the
    configuration data. Upon saving, it responds with a success message or
    an error message if the saving process fails.
    """
    redirect_port = random.randint(30000, 50000)
    server_url = f"http://localhost:{redirect_port}"
    
    print(f"Starting configuration server on {server_url}")
    
    class ConfigHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            """Handle HTTP GET requests for the server.

            This method processes incoming GET requests. If the request path is the
            root ("/"), it responds with a 200 status code and serves an HTML
            template. If the request path is anything else, it responds with a 404
            status code indicating that the resource was not found.
            """

            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                # Read the template HTML file
                template_path = pkg_resources.resource_filename(
                    "penify_hook", "templates/llm_config.html"
                )
                
                with open(template_path, 'r') as f:
                    content = f.read()
                
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not Found")

        def do_POST(self):
            """Handle POST requests to save LLM configuration.

            This method processes incoming POST requests directed to the "/save"
            path. It reads the request body to extract the model configuration
            details, including the model name, API base URL, and API key. Upon
            successful saving of the configuration, it sends a success response and
            initiates a server shutdown in a separate thread. If an error occurs
            during the saving process, it responds with an error message. If the
            request path is not recognized, it returns a 404 Not Found response.
            """

            if self.path == "/save":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())
                
                model = data.get('model')
                api_base = data.get('api_base')
                api_key = data.get('api_key')
                
                try:
                    save_llm_config(model, api_base, api_key)
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = {
                        "success": True, 
                        "message": f"LLM configuration saved successfully. Using model: {model}"
                    }
                    self.wfile.write(json.dumps(response).encode())
                    
                    # Schedule the server shutdown
                    thread = Thread(target=self.server.shutdown)
                    thread.daemon = True
                    thread.start()
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = {"success": False, "message": f"Error saving configuration: {str(e)}"}
                    self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Not Found"}).encode())
        
        def log_message(self, format, *args):
            # Suppress log messages
            return

    with socketserver.TCPServer(("", redirect_port), ConfigHandler) as httpd:
        print(f"Opening configuration page in your browser...")
        webbrowser.open(server_url)
        print(f"Waiting for configuration to be submitted...")
        httpd.serve_forever()
    
    print("Configuration completed.")

def config_jira_web():
    """Open a web browser interface for configuring JIRA settings.

    This function sets up a simple HTTP server that serves a configuration
    page for JIRA settings. It generates a random port number for the server
    and opens the configuration page in the user's default web browser. The
    user can submit their JIRA configuration details, which are then
    processed and saved. The server handles both GET and POST requests,
    providing appropriate responses based on the user's actions.  The GET
    request serves an HTML template for the configuration page, while the
    POST request processes the submitted configuration data, saves it, and
    responds with success or error messages.
    """
    # Similar implementation to config_llm_web but for JIRA settings
    redirect_port = random.randint(30000, 50000)
    server_url = f"http://localhost:{redirect_port}"
    
    print(f"Starting configuration server on {server_url}")
    
    class ConfigHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            """Handle HTTP GET requests for the server.

            This method processes incoming GET requests. If the request path is the
            root ("/"), it sends a 200 response along with the content of the HTML
            template file. If the request path is anything else, it sends a 404
            response indicating that the requested resource was not found.
            """

            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                
                # Read the template HTML file
                template_path = pkg_resources.resource_filename(
                    "penify_hook", "templates/jira_config.html"
                )
                
                with open(template_path, 'r') as f:
                    content = f.read()
                
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not Found")

        def do_POST(self):
            """Handle POST requests to save JIRA configuration.

            This method processes incoming POST requests to the "/save" endpoint. It
            reads the request body, extracts the necessary configuration data such
            as the JIRA URL, username, and API token, and attempts to save this
            configuration using the `save_jira_config` function. If the
            configuration is saved successfully, it sends a success response and
            initiates a server shutdown in a separate thread. If an error occurs
            during the saving process, it sends an error response with the
            appropriate message. If the request path is not recognized, it returns a
            404 Not Found response.
            """

            if self.path == "/save":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())
                
                url = data.get('url')
                username = data.get('username')
                api_token = data.get('api_token')
                verify = data.get('verify', False)
                
                try:
                    # Save the configuration
                    save_jira_config(url, username, api_token)
                    
                    # Verify connection option is handled in main.py
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = {
                        "success": True, 
                        "message": f"JIRA configuration saved successfully."
                    }
                    self.wfile.write(json.dumps(response).encode())
                    
                    # Schedule the server shutdown
                    thread = Thread(target=self.server.shutdown)
                    thread.daemon = True
                    thread.start()
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    response = {"success": False, "message": f"Error saving configuration: {str(e)}"}
                    self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Not Found"}).encode())
        
        def log_message(self, format, *args):
            # Suppress log messages
            return

    with socketserver.TCPServer(("", redirect_port), ConfigHandler) as httpd:
        print(f"Opening configuration page in your browser...")
        webbrowser.open(server_url)
        print(f"Waiting for configuration to be submitted...")
        httpd.serve_forever()
    
    print("Configuration completed.")

def get_token(passed_token):
    """Get the token based on priority.

    This function retrieves an API token by checking multiple sources in a
    specific order. It first checks if a token is passed as an argument. If
    not, it looks for an environment variable named 'PENIFY_API_TOKEN'. If
    the environment variable is not set, it attempts to read the token from
    a configuration file located at the user's home directory named
    '.penify'. If the configuration file exists and is readable, it tries to
    load the JSON content and retrieve the 'api_keys' value. If any errors
    occur during this process, they are printed to the console.

    Args:
        passed_token (str): An optional token that can be provided directly.

    Returns:
        str or None: The retrieved token if found, otherwise None.
    """
    if passed_token:
        return passed_token
    
    import os
    env_token = os.getenv('PENIFY_API_TOKEN')
    if env_token:
        return env_token
    
    config_file = Path.home() / '.penify'
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_keys')
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading .penify config file: {str(e)}")
    
    return None
