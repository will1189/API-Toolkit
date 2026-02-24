import argparse
import json
import sys
import http_client as http
import formatter as fmt
import storage as db

def parse_headers(headers_str):
    if not headers_str:
        return {}
    headers = {}
    for item in headers_str.split(','):
        if ':' in item:
            key, value = item.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def parse_data(data_str):
    if not data_str:
        return {}
    data = {}
    for item in data_str.split(','):
        if '=' in item:
            key, value = item.split('=', 1)
            data[key.strip()] = value.strip()
    return data

def cmd_request(args):
    method = args.method.upper()
    url = args.url
    
    if not url:
        print("Error: URL is required")
        return
    
    headers = parse_headers(args.headers) if args.headers else {}
    params = parse_data(args.params) if args.params else {}
    body = args.body
    
    auth_type = 'none'
    auth_data = {}
    
    if args.auth_basic:
        auth_type = 'basic'
        if ':' in args.auth_basic:
            username, password = args.auth_basic.split(':', 1)
            auth_data = {'username': username, 'password': password}
    
    if args.auth_bearer:
        auth_type = 'bearer'
        auth_data = {'token': args.auth_bearer}
    
    if args.auth_api_key:
        auth_type = 'api_key'
        if ':' in args.auth_api_key:
            key_name, key_value = args.auth_api_key.split(':', 1)
            auth_data = {'key_name': key_name, 'key_value': key_value}
    
    env = db.get_active_environment()
    variables = env.get('variables', {}) if env else {}
    
    if args.var:
        for v in args.var:
            if '=' in v:
                key, value = v.split('=', 1)
                variables[key] = value
    
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

def cmd_history(args):
    limit = args.limit
    history = db.get_history(limit)
    
    if not history:
        print("No history found")
        return
    
    print(f"\n{'#':<4} {'Method':<8} {'Status':<8} {'URL':<45} {'Time':<10}")
    print("-" * 85)
    
    for i, item in enumerate(history, 1):
        method = item['method']
        method_color = fmt.METHOD_COLORS.get(method, '')
        
        status = item['response_status']
        if status:
            status_color = fmt.get_status_color(status)
            status_str = f"{status_color}{status}{fmt.STATUS_COLORS['RESET']}"
        else:
            status_str = "--"
        
        url = item['url']
        if len(url) > 45:
            url = url[:42] + '...'
        
        time_ms = f"{item['response_time']:.0f}ms" if item['response_time'] else "--"
        
        print(f"{i:<4} {method_color}{method}{fmt.METHOD_COLORS['RESET']:<5} {status_str:<8} {url:<45} {time_ms:<10}")

def cmd_history_clear(args):
    db.clear_history()
    print("History cleared")

def cmd_env_list(args):
    envs = db.get_environments()
    
    if not envs:
        print("No environments found")
        return
    
    active_env = db.get_active_environment()
    
    print("\nEnvironments:")
    for env in envs:
        active_marker = " (active)" if active_env and env['id'] == active_env['id'] else ""
        print(f"  [{env['id']}] {env['name']}{active_marker}")
        variables = json.loads(env['variables'] or '{}')
        for key, value in variables.items():
            print(f"      {key} = {value}")

def cmd_env_create(args):
    name = args.name
    variables = parse_data(args.vars[0]) if args.vars else {}
    
    db.save_environment(name, variables)
    print(f"Environment '{name}' created and activated")

def cmd_env_use(args):
    env_id = args.id
    db.set_active_environment(env_id)
    print(f"Environment [{env_id}] is now active")

def cmd_env_delete(args):
    env_id = args.id
    db.delete_environment(env_id)
    print(f"Environment [{env_id}] deleted")

def cmd_env_show(args):
    env = db.get_active_environment()
    if env:
        print(f"\nActive Environment: {env['name']}")
        print("Variables:")
        for key, value in env.get('variables', {}).items():
            print(f"  {key} = {value}")
    else:
        print("No active environment")

def cmd_save(args):
    if not args.name or not args.url:
        print("Error: --name and --url are required")
        return
    
    method = args.method.upper()
    url = args.url
    headers = parse_headers(args.headers) if args.headers else {}
    body = args.body
    params = parse_data(args.params) if args.params else {}
    
    auth_type = 'none'
    auth_data = {}
    
    if args.auth_basic:
        auth_type = 'basic'
        if ':' in args.auth_basic:
            username, password = args.auth_basic.split(':', 1)
            auth_data = {'username': username, 'password': password}
    
    if args.auth_bearer:
        auth_type = 'bearer'
        auth_data = {'token': args.auth_bearer}
    
    if args.auth_api_key:
        auth_type = 'api_key'
        if ':' in args.auth_api_key:
            key_name, key_value = args.auth_api_key.split(':', 1)
            auth_data = {'key_name': key_name, 'key_value': key_value}
    
    db.save_request(args.name, method, url, headers, body, params, auth_type, auth_data)
    print(f"Request '{args.name}' saved")

def cmd_load(args):
    req_id = args.id
    req = db.get_saved_request(req_id)
    
    if not req:
        print(f"Request [{req_id}] not found")
        return
    
    print(f"\nLoading request: {req['name']}")
    print(f"{fmt.METHOD_COLORS.get(req['method'], '')}{req['method']}{fmt.METHOD_COLORS['RESET']} {req['url']}")
    
    env = db.get_active_environment()
    variables = env.get('variables', {}) if env else {}
    
    response = http.send_request(
        method=req['method'],
        url=req['url'],
        headers=req.get('headers'),
        params=req.get('params'),
        body=req.get('body'),
        auth_type=req.get('auth_type', 'none'),
        auth_data=req.get('auth_data'),
        variables=variables
    )
    
    db.add_to_history(req['method'], req['url'], req.get('headers'), req.get('body'), req.get('params'), response)
    fmt.print_response(response)

def cmd_saved_list(args):
    requests = db.get_saved_requests()
    
    if not requests:
        print("No saved requests")
        return
    
    print(f"\n{'#':<4} {'Name':<20} {'Method':<8} {'URL':<50}")
    print("-" * 90)
    
    for req in requests:
        method_color = fmt.METHOD_COLORS.get(req['method'], '')
        name = req['name'][:20]
        url = req['url']
        if len(url) > 50:
            url = url[:47] + '...'
        print(f"[{req['id']:<2}] {name:<20} {method_color}{req['method']}{fmt.METHOD_COLORS['RESET']:<5} {url}")

def cmd_saved_delete(args):
    req_id = args.id
    db.delete_saved_request(req_id)
    print(f"Request [{req_id}] deleted")

def main():
    parser = argparse.ArgumentParser(description='API Toolkit - Command Line API Debugger')
    parser.add_argument('--version', action='version', version='API Toolkit v1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    req_parser = subparsers.add_parser('request', help='Send HTTP request')
    req_parser.add_argument('method', choices=http.METHODS, help='HTTP method')
    req_parser.add_argument('url', help='Request URL')
    req_parser.add_argument('-H', '--headers', help='Headers (format: key:value,key2:value2)')
    req_parser.add_argument('-d', '--body', help='Request body')
    req_parser.add_argument('-p', '--params', help='URL params (format: key=value,key2=value2)')
    req_parser.add_argument('--auth-basic', help='Basic auth (format: username:password)')
    req_parser.add_argument('--auth-bearer', help='Bearer token')
    req_parser.add_argument('--auth-api-key', help='API key (format: key_name:key_value)')
    req_parser.add_argument('--var', action='append', help='Variable (format: key=value)')
    req_parser.set_defaults(func=cmd_request)
    
    hist_parser = subparsers.add_parser('history', help='View request history')
    hist_parser.add_argument('-n', '--limit', type=int, default=20, help='Number of items to show')
    hist_parser.set_defaults(func=cmd_history)
    
    hist_clear_parser = subparsers.add_parser('history-clear', help='Clear history')
    hist_clear_parser.set_defaults(func=cmd_history_clear)
    
    env_parser = subparsers.add_parser('env', help='Environment management')
    env_subparsers = env_parser.add_subparsers(dest='env_command')
    
    env_list_parser = env_subparsers.add_parser('list', help='List environments')
    env_list_parser.set_defaults(func=cmd_env_list)
    
    env_create_parser = env_subparsers.add_parser('create', help='Create environment')
    env_create_parser.add_argument('name', help='Environment name')
    env_create_parser.add_argument('vars', nargs='*', help='Variables (format: key=value)')
    env_create_parser.set_defaults(func=cmd_env_create)
    
    env_use_parser = env_subparsers.add_parser('use', help='Set active environment')
    env_use_parser.add_argument('id', type=int, help='Environment ID')
    env_use_parser.set_defaults(func=cmd_env_use)
    
    env_delete_parser = env_subparsers.add_parser('delete', help='Delete environment')
    env_delete_parser.add_argument('id', type=int, help='Environment ID')
    env_delete_parser.set_defaults(func=cmd_env_delete)
    
    env_show_parser = env_subparsers.add_parser('show', help='Show active environment')
    env_show_parser.set_defaults(func=cmd_env_show)
    
    save_parser = subparsers.add_parser('save', help='Save request')
    save_parser.add_argument('--name', required=True, help='Request name')
    save_parser.add_argument('--method', default='GET', choices=http.METHODS, help='HTTP method')
    save_parser.add_argument('--url', required=True, help='Request URL')
    save_parser.add_argument('-H', '--headers', help='Headers')
    save_parser.add_argument('-d', '--body', help='Request body')
    save_parser.add_argument('-p', '--params', help='URL params')
    save_parser.add_argument('--auth-basic', help='Basic auth')
    save_parser.add_argument('--auth-bearer', help='Bearer token')
    save_parser.add_argument('--auth-api-key', help='API key')
    save_parser.set_defaults(func=cmd_save)
    
    load_parser = subparsers.add_parser('load', help='Load and execute saved request')
    load_parser.add_argument('id', type=int, help='Request ID')
    load_parser.set_defaults(func=cmd_load)
    
    saved_list_parser = subparsers.add_parser('saved', help='List saved requests')
    saved_list_parser.set_defaults(func=cmd_saved_list)
    
    saved_delete_parser = subparsers.add_parser('saved-delete', help='Delete saved request')
    saved_delete_parser.add_argument('id', type=int, help='Request ID')
    saved_delete_parser.set_defaults(func=cmd_saved_delete)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if hasattr(args, 'env_command'):
        if args.env_command == 'list':
            cmd_env_list(args)
        elif args.env_command == 'create':
            cmd_env_create(args)
        elif args.env_command == 'use':
            cmd_env_use(args)
        elif args.env_command == 'delete':
            cmd_env_delete(args)
        elif args.env_command == 'show':
            cmd_env_show(args)
        else:
            env_parser.print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    db.init_database()
    main()
