import json
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

METHOD_COLORS = {
    'GET': Fore.CYAN,
    'POST': Fore.GREEN,
    'PUT': Fore.YELLOW,
    'PATCH': Fore.MAGENTA,
    'DELETE': Fore.RED,
    'HEAD': Fore.BLUE,
    'OPTIONS': Fore.WHITE,
    'RESET': Style.RESET_ALL
}

STATUS_COLORS = {
    '2xx': Fore.GREEN,
    '3xx': Fore.YELLOW,
    '4xx': Fore.RED,
    '5xx': Fore.RED + Style.BRIGHT,
    'RESET': Style.RESET_ALL
}

def get_status_color(status_code):
    if 200 <= status_code < 300:
        return STATUS_COLORS['2xx']
    elif 300 <= status_code < 400:
        return STATUS_COLORS['3xx']
    elif 400 <= status_code < 500:
        return STATUS_COLORS['4xx']
    elif 500 <= status_code < 600:
        return STATUS_COLORS['5xx']
    return ''

def format_json(data, indent=2):
    try:
        if isinstance(data, str):
            data = json.loads(data)
        return json.dumps(data, indent=indent, ensure_ascii=False)
    except:
        return str(data)

def print_response(response):
    print()
    print("=" * 60)
    
    method = response.get('method', 'GET')
    method_color = METHOD_COLORS.get(method, '')
    print(f"{method_color}{method}{METHOD_COLORS['RESET']} {response.get('url', '')}")
    
    if response.get('error'):
        print(f"{Fore.RED}Error: {response['error']}{Fore.RESET}")
        print("=" * 60)
        return
    
    status_code = response.get('status_code')
    if status_code:
        status_color = get_status_color(status_code)
        print(f"Status: {status_color}{status_code}{STATUS_COLORS['RESET']}")
    
    elapsed = response.get('elapsed_ms', 0)
    print(f"Time: {elapsed:.2f}ms")
    
    print("-" * 60)
    print(f"{Fore.WHITE}Headers:{Fore.RESET}")
    headers = response.get('headers', {})
    if headers:
        for key, value in headers.items():
            print(f"  {key}: {value}")
    else:
        print("  (none)")
    
    print("-" * 60)
    print(f"{Fore.WHITE}Body:{Fore.RESET}")
    body = response.get('body')
    if body:
        if isinstance(body, (dict, list)):
            print(format_json(body))
        else:
            try:
                print(format_json(body))
            except:
                print(body)
    else:
        print("  (empty)")
    
    print("=" * 60)

def print_request_summary(method, url, headers=None, params=None, body=None):
    method_color = METHOD_COLORS.get(method.upper(), '')
    print(f"\n{method_color}{method.upper()}{METHOD_COLORS['RESET']} {url}")
    
    if params:
        print(f"Params: {params}")
    
    if headers:
        print("Headers:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
    
    if body:
        print(f"Body: {body}")
