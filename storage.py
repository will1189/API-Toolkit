import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'api_toolkit.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT NOT NULL,
            url TEXT NOT NULL,
            headers TEXT,
            body TEXT,
            params TEXT,
            response_status INTEGER,
            response_body TEXT,
            response_headers TEXT,
            response_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS environments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            variables TEXT,
            is_active INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            method TEXT NOT NULL,
            url TEXT NOT NULL,
            headers TEXT,
            body TEXT,
            params TEXT,
            auth_type TEXT,
            auth_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_to_history(method, url, headers, body, params, response):
    conn = get_connection()
    cursor = conn.cursor()
    
    response_status = response.get('status_code')
    response_body = response.get('body')
    response_headers = response.get('headers')
    response_time = response.get('elapsed_ms')
    
    if isinstance(response_body, (dict, list)):
        response_body = json.dumps(response_body)
    if isinstance(response_headers, dict):
        response_headers = json.dumps(response_headers)
    
    cursor.execute('''
        INSERT INTO history (method, url, headers, body, params, response_status, response_body, response_headers, response_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (method, url, json.dumps(headers), body, json.dumps(params), response_status, response_body, response_headers, response_time))
    
    conn.commit()
    conn.close()

def get_history(limit=20):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_history():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM history')
    conn.commit()
    conn.close()

def save_environment(name, variables):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE environments SET is_active = 0')
    cursor.execute('INSERT INTO environments (name, variables, is_active) VALUES (?, ?, 1)', 
                  (name, json.dumps(variables)))
    conn.commit()
    conn.close()

def get_environments():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM environments ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_active_environment():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM environments WHERE is_active = 1')
    row = cursor.fetchone()
    conn.close()
    if row:
        env = dict(row)
        env['variables'] = json.loads(env['variables'] or '{}')
        return env
    return None

def set_active_environment(env_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE environments SET is_active = 0')
    cursor.execute('UPDATE environments SET is_active = 1 WHERE id = ?', (env_id,))
    conn.commit()
    conn.close()

def delete_environment(env_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM environments WHERE id = ?', (env_id,))
    conn.commit()
    conn.close()

def save_request(name, method, url, headers=None, body=None, params=None, auth_type='none', auth_data=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO saved_requests (name, method, url, headers, body, params, auth_type, auth_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, method, url, json.dumps(headers), body, json.dumps(params), auth_type, json.dumps(auth_data)))
    conn.commit()
    conn.close()

def get_saved_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_requests ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_saved_request(req_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM saved_requests WHERE id = ?', (req_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        req = dict(row)
        req['headers'] = json.loads(req['headers'] or '{}')
        req['params'] = json.loads(req['params'] or '{}')
        req['auth_data'] = json.loads(req['auth_data'] or '{}')
        return req
    return None

def delete_saved_request(req_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM saved_requests WHERE id = ?', (req_id,))
    conn.commit()
    conn.close()
