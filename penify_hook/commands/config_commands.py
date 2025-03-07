import json
import os
import random
import webbrowser
import http.server
import socketserver
import pkg_resources
from pathlib import Path
from threading import Thread
import logging


def get_penify_config() -> Path:
    """
    Get the home directory for the .penify configuration file.
    This function searches for the .penify file in the current directory
    and its parent directories until it finds it or reaches the home directory.
    """
    from penify_hook.utils import recursive_search_git_folder

    current_dir = os.getcwd()
    home_dir = recursive_search_git_folder(current_dir)
    

    if not home_dir:
        home_dir = Path.home()
    else:
        home_dir = Path(home_dir)

    penify_dir = home_dir / '.penify'
    if penify_dir.exists():
        return penify_dir / 'config.json'
    else:
        # Create the .penify directory if it doesn't exist
        os.makedirs(penify_dir, exist_ok=True)
        ## update gitignore
        
        # Create the .penify directory
        os.makedirs(penify_dir, exist_ok=True)        
        # Create an empty config.json file
        with open(penify_dir / 'config.json', 'w') as f:
            json.dump({}, f)
    return penify_dir / 'config.json'
    

def save_llm_config(model, api_base, api_key):
    """
    Save LLM configuration settings in the .penify file.
    """

    penify_file = get_penify_config()
    
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
    """
    Save JIRA configuration settings in the .penify file.
    """
    from penify_hook.utils import recursive_search_git_folder

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
    """
    Get LLM configuration from the .penify file.
    """
    config_file = get_penify_config()
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('llm', {})
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading .penify config file: {str(e)}")
    
    return {}

def get_jira_config():
    """
    Get JIRA configuration from the .penify file.
    """
    config_file = get_penify_config()
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('jira', {})
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading .penify config file: {str(e)}")
    
    return {}

def config_llm_web():
    """
    Open a web browser interface for configuring LLM settings.
    """
    redirect_port = random.randint(30000, 50000)
    server_url = f"http://localhost:{redirect_port}"
    
    print(f"Starting configuration server on {server_url}")
    
    class ConfigHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
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
            elif self.path == "/get_config":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                # Get current LLM configuration
                current_config = get_llm_config()
                
                if current_config:
                    response = {
                        "success": True,
                        "config": current_config
                    }
                else:
                    response = {
                        "success": False,
                        "message": "No configuration found"
                    }
                
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not Found")

        def do_POST(self):
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
    """
    Open a web browser interface for configuring JIRA settings.
    """
    redirect_port = random.randint(30000, 50000)
    server_url = f"http://localhost:{redirect_port}"
    
    print(f"Starting configuration server on {server_url}")
    
    class ConfigHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
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
            elif self.path == "/get_config":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                
                # Get current JIRA configuration
                current_config = get_jira_config()
                
                if current_config:
                    response = {
                        "success": True,
                        "config": current_config
                    }
                else:
                    response = {
                        "success": False,
                        "message": "No JIRA configuration found"
                    }
                
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Not Found")

        def do_POST(self):
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

def get_token():
    """
    Get the token based on priority.
    """
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
