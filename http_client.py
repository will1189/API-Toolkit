import requests
import json
import time
from urllib.parse import urlparse, parse_qs

METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

def build_headers(headers_dict=None, auth_type=None, auth_data=None):
    headers = headers_dict or {}
    
    if auth_type == 'basic':
        from requests.auth import HTTPBasicAuth
        username = auth_data.get('username', '')
        password = auth_data.get('password', '')
        auth = HTTPBasicAuth(username, password)
    elif auth_type == 'bearer':
        token = auth_data.get('token', '')
        headers['Authorization'] = f'Bearer {token}'
    elif auth_type == 'api_key':
        key_name = auth_data.get('key_name', 'X-API-Key')
        key_value = auth_data.get('key_value', '')
        key_location = auth_data.get('key_location', 'header')
        if key_location == 'header':
            headers[key_name] = key_value
    
    return headers

def interpolate_variables(text, variables):
    if not text or not variables:
        return text
    
    result = text
    for key, value in variables.items():
        result = result.replace(f'{{{{{key}}}}}', str(value))
    
    return result

def send_request(method, url, headers=None, params=None, body=None, 
                 auth_type='none', auth_data=None, timeout=30, variables=None):
    start_time = time.time()
    
    url = interpolate_variables(url, variables)
    headers = headers or {}
    params = params or {}
    
    headers = build_headers(headers, auth_type, auth_data)
    
    if variables:
        for key, value in variables.items():
            if isinstance(headers, dict):
                for h_key, h_value in headers.items():
                    if isinstance(h_value, str):
                        headers[h_key] = h_value.replace(f'{{{{{key}}}}}', str(value))
            if isinstance(params, dict):
                for p_key, p_value in params.items():
                    if isinstance(p_value, str):
                        params[p_key] = p_value.replace(f'{{{{{key}}}}}', str(value))
    
    request_body = body
    if body and variables:
        request_body = interpolate_variables(body, variables)
        try:
            body_dict = json.loads(request_body)
            for key, value in variables.items():
                if isinstance(value, str):
                    for b_key, b_value in body_dict.items():
                        if isinstance(b_value, str):
                            body_dict[b_key] = b_value.replace(f'{{{{{key}}}}}', str(value))
            request_body = json.dumps(body_dict)
        except:
            pass
    
    response = None
    error = None
    response_status = None
    response_headers = None
    response_body = None
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, headers=headers, params=params, data=request_body, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, params=params, data=request_body, timeout=timeout)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, params=params, data=request_body, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params, timeout=timeout)
        elif method == 'HEAD':
            response = requests.head(url, headers=headers, params=params, timeout=timeout)
        elif method == 'OPTIONS':
            response = requests.options(url, headers=headers, params=params, timeout=timeout)
        
        if response is not None:
            response_status = response.status_code
            response_headers = dict(response.headers)
            try:
                response_body = response.json()
            except:
                response_body = response.text
            
            if response_status >= 400:
                try:
                    error = response.json()
                except:
                    error = response.text
    except requests.exceptions.Timeout:
        error = 'Request timeout'
    except requests.exceptions.ConnectionError:
        error = 'Connection error'
    except requests.exceptions.RequestException as e:
        error = str(e)
    
    elapsed_time = (time.time() - start_time) * 1000
    
    return {
        'method': method,
        'url': url,
        'status_code': response_status,
        'headers': response_headers,
        'body': response_body,
        'elapsed_ms': elapsed_time,
        'error': error,
        'raw_response': response
    }
