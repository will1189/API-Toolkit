import sys
import os
import json
import http_client as http
import formatter as fmt
import storage as db
import shlex

class InteractiveShell:
    def __init__(self):
        self.running = True
        self.current_env = db.get_active_environment()
        self.variables = self.current_env.get('variables', {}) if self.current_env else {}
    
    def print_banner(self):
        print("\n" + "=" * 60)
        print("  API Toolkit - Interactive Mode")
        print("  Type 'help' for available commands")
        print("=" * 60)
        if self.current_env:
            print(f"Environment: {self.current_env['name']}")
        print()
    
    def print_help(self):
        print("\nAvailable commands:")
        print("  request <method> <url>        - Send HTTP request")
        print("  get <url>                    - GET request")
        print("  post <url> [body]            - POST request")
        print("  put <url> [body]             - PUT request")
        print("  delete <url>                 - DELETE request")
        print("  patch <url> [body]           - PATCH request")
        print("  header <key>:<value>        - Set header")
        print("  param <key>=<value>         - Set parameter")
        print("  auth basic <user>:<pass>     - Basic auth")
        print("  auth bearer <token>         - Bearer token")
        print("  auth api <key>:<value>      - API key")
        print("  var <key>=<value>           - Set variable")
        print("  env                          - Show current environment")
        print("  env list                     - List environments")
        print("  env create <name>           - Create environment")
        print("  env use <id>                - Switch environment")
        print("  history [-n count]          - Show history")
        print("  save <name>                 - Save current request")
        print("  saved                       - List saved requests")
        print("  load <id>                    - Load saved request")
        print("  clear                        - Clear output")
        print("  exit                         - Exit")
        print()
    
    def parse_command(self, line):
        try:
            parts = shlex.split(line)
        except:
            parts = line.split()
        
        if not parts:
            return
        
        cmd = parts[0].lower()
        
        if cmd == 'help':
            self.print_help()
        
        elif cmd == 'exit' or cmd == 'quit':
            self.running = False
            print("Goodbye!")
        
        elif cmd == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
        
        elif cmd == 'request':
            if len(parts) < 3:
                print("Usage: request <method> <url>")
                return
            method = parts[1].upper()
            url = parts[2]
            self.send_request(method, url)
        
        elif cmd in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
            if len(parts) < 2:
                print(f"Usage: {cmd} <url> [body]")
                return
            url = parts[1]
            body = parts[2] if len(parts) > 2 else None
            self.send_request(cmd.upper(), url, body)
        
        elif cmd == 'header':
            if len(parts) < 2:
                print("Usage: header <key>:<value>")
                return
            if ':' in parts[1]:
                key, value = parts[1].split(':', 1)
                self.headers[key.strip()] = value.strip()
                print(f"Header set: {key} = {value}")
        
        elif cmd == 'param':
            if len(parts) < 2 or '=' not in parts[1]:
                print("Usage: param <key>=<value>")
                return
            key, value = parts[1].split('=', 1)
            self.params[key.strip()] = value.strip()
            print(f"Param set: {key} = {value}")
        
        elif cmd == 'auth':
            if len(parts) < 2:
                print("Usage: auth <type> [value]")
                return
            auth_type = parts[1].lower()
            if auth_type == 'basic' and len(parts) > 2:
                if ':' in parts[2]:
                    username, password = parts[2].split(':', 1)
                    self.auth_type = 'basic'
                    self.auth_data = {'username': username, 'password': password}
                    print(f"Basic auth set for user: {username}")
            elif auth_type == 'bearer' and len(parts) > 2:
                self.auth_type = 'bearer'
                self.auth_data = {'token': parts[2]}
                print("Bearer token set")
            elif auth_type == 'api' and len(parts) > 2:
                if ':' in parts[2]:
                    key_name, key_value = parts[2].split(':', 1)
                    self.auth_type = 'api_key'
                    self.auth_data = {'key_name': key_name, 'key_value': key_value}
                    print(f"API key set: {key_name}")
        
        elif cmd == 'var':
            if len(parts) < 2 or '=' not in parts[1]:
                print("Usage: var <key>=<value>")
                return
            key, value = parts[1].split('=', 1)
            self.variables[key.strip()] = value.strip()
            print(f"Variable set: {key} = {value}")
        
        elif cmd == 'env':
            if len(parts) > 1 and parts[1] == 'list':
                self.cmd_env_list()
            elif len(parts) > 1 and parts[1] == 'create':
                if len(parts) > 2:
                    name = parts[2]
                    db.save_environment(name, {})
                    print(f"Environment '{name}' created")
            elif len(parts) > 1 and parts[1] == 'use':
                if len(parts) > 2:
                    try:
                        env_id = int(parts[2])
                        db.set_active_environment(env_id)
                        self.current_env = db.get_active_environment()
                        self.variables = self.current_env.get('variables', {}) if self.current_env else {}
                        print(f"Environment [{env_id}] activated")
                    except:
                        print("Invalid environment ID")
            else:
                self.cmd_env_show()
        
        elif cmd == 'history':
            limit = 20
            if len(parts) > 1 and parts[1] == '-n':
                if len(parts) > 2:
                    try:
                        limit = int(parts[2])
                    except:
                        pass
            self.cmd_history(limit)
        
        elif cmd == 'save':
            if len(parts) < 2:
                print("Usage: save <name>")
                return
            name = parts[1]
            if not hasattr(self, 'current_url') or not self.current_url:
                print("No request to save. Use 'request' command first.")
                return
            db.save_request(
                name,
                getattr(self, 'current_method', 'GET'),
                getattr(self, 'current_url', ''),
                getattr(self, 'headers', {}),
                getattr(self, 'current_body', None),
                getattr(self, 'params', {}),
                getattr(self, 'auth_type', 'none'),
                getattr(self, 'auth_data', {})
            )
            print(f"Request '{name}' saved")
        
        elif cmd == 'saved':
            self.cmd_saved_list()
        
        elif cmd == 'load':
            if len(parts) < 2:
                print("Usage: load <id>")
                return
            try:
                req_id = int(parts[1])
                self.cmd_load(req_id)
            except:
                print("Invalid request ID")
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")
    
    def send_request(self, method, url, body=None):
        self.current_method = method
        self.current_url = url
        self.current_body = body
        
        headers = getattr(self, 'headers', {})
        params = getattr(self, 'params', {})
        auth_type = getattr(self, 'auth_type', 'none')
        auth_data = getattr(self, 'auth_data', {})
        variables = self.variables
        
        fmt.print_request_summary(method, url, headers, params, body)
        
        response = http.send_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            body=body,
            auth_type=auth_type,
            auth_data=auth_data,
            variables=variables
        )
        
        db.add_to_history(method, url, headers, body, params, response)
        fmt.print_response(response)
    
    def cmd_env_show(self):
        if self.current_env:
            print(f"\nActive Environment: {self.current_env['name']}")
            print("Variables:")
            for key, value in self.variables.items():
                print(f"  {key} = {value}")
        else:
            print("No active environment")
    
    def cmd_env_list(self):
        envs = db.get_environments()
        if not envs:
            print("No environments")
            return
        active_env = db.get_active_environment()
        print("\nEnvironments:")
        for env in envs:
            marker = " (active)" if active_env and env['id'] == active_env['id'] else ""
            print(f"  [{env['id']}] {env['name']}{marker}")
    
    def cmd_history(self, limit=20):
        history = db.get_history(limit)
        if not history:
            print("No history")
            return
        print(f"\n{'#':<4} {'Method':<8} {'Status':<8} {'URL':<45} {'Time':<10}")
        print("-" * 85)
        for i, item in enumerate(history, 1):
            method = item['method']
            method_color = fmt.METHOD_COLORS.get(method, '')
            status = item['response_status']
            status_str = str(status) if status else "--"
            status_color = fmt.get_status_color(status) if status else ""
            url = item['url'][:42] + '...' if len(item['url']) > 45 else item['url']
            time_str = f"{item['response_time']:.0f}ms" if item['response_time'] else "--"
            print(f"{i:<4} {method_color}{method}{fmt.METHOD_COLORS['RESET']:<5} {status_color}{status_str}{fmt.STATUS_COLORS['RESET']:<5} {url:<45} {time_str:<10}")
    
    def cmd_saved_list(self):
        requests = db.get_saved_requests()
        if not requests:
            print("No saved requests")
            return
        print(f"\n{'#':<4} {'Name':<20} {'Method':<8} {'URL':<50}")
        print("-" * 90)
        for req in requests:
            method_color = fmt.METHOD_COLORS.get(req['method'], '')
            name = req['name'][:20]
            url = req['url'][:47] + '...' if len(req['url']) > 50 else req['url']
            print(f"[{req['id']:<2}] {name:<20} {method_color}{req['method']}{fmt.METHOD_COLORS['RESET']:<5} {url}")
    
    def cmd_load(self, req_id):
        req = db.get_saved_request(req_id)
        if not req:
            print(f"Request [{req_id}] not found")
            return
        print(f"\nLoading: {req['name']}")
        self.headers = req.get('headers', {})
        self.params = req.get('params', {})
        self.auth_type = req.get('auth_type', 'none')
        self.auth_data = req.get('auth_data', {})
        self.send_request(req['method'], req['url'], req.get('body'))
    
    def reset_request_state(self):
        self.headers = {}
        self.params = {}
        self.auth_type = 'none'
        self.auth_data = {}
        self.current_method = None
        self.current_url = None
        self.current_body = None
    
    def run(self):
        self.headers = {}
        self.params = {}
        self.auth_type = 'none'
        self.auth_data = {}
        
        self.print_banner()
        
        while self.running:
            try:
                line = input("api> ").strip()
                if line:
                    self.parse_command(line)
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                break

def main():
    db.init_database()
    shell = InteractiveShell()
    shell.run()

if __name__ == '__main__':
    main()
