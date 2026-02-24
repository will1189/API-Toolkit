# API Toolkit

[![GitHub](https://img.shields.io/badge/GitHub-API--Toolkit-blue?style=flat-square&logo=github)](https://github.com/will1189/API-Toolkit)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

A powerful command-line API debugging tool for developers.

## Features

- **Multiple HTTP Methods**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- **Authentication**: Basic Auth, Bearer Token, API Key
- **Custom Headers**: Flexible configuration of headers and URL parameters
- **Variable Interpolation**: Use `{{variable}}` syntax in requests
- **Environment Management**: Switch between multiple environments
- **Request History**: Automatic saving of all requests
- **Save & Load**: Bookmark frequently used requests
- **Colorful Output**: Formatted JSON response display
- **Interactive Shell**: User-friendly interactive mode

## Installation

```bash
# Clone the repository
git clone https://github.com/will1189/API-Toolkit.git

# Install dependencies
cd api_toolkit
pip install -r requirements.txt
```

## Quick Start

### Command Line Mode

```bash
# Send a GET request
python main.py request GET https://httpbin.org/get

# Send a POST request with JSON body
python main.py request POST https://httpbin.org/post -d '{"name":"test"}'

# Custom headers
python main.py request GET https://api.example.com/users -H "Authorization:Bearer token"

# URL parameters
python main.py request GET https://api.example.com/users -p "page=1&size=10"

# Basic Authentication
python main.py request GET https://api.example.com/protected --auth-basic username:password

# Bearer Token
python main.py request GET https://api.example.com/protected --auth-bearer your_token_here

# API Key
python main.py request GET https://api.example.com/protected --auth-api-key X-API-Key:your_key
```

### Interactive Shell Mode

```bash
python shell.py
```

```
api> help
api> get https://httpbin.org/get
api> post https://httpbin.org/post -d '{"name":"test"}'
api> header Content-Type:application/json
api> var API_URL=https://api.example.com
api> history
api> exit
```

## Commands

### Request Options

| Option | Description |
|--------|-------------|
| `-H, --headers` | Request headers (format: key:value,key2:value2) |
| `-d, --body` | Request body |
| `-p, --params` | URL parameters (format: key=value,key2=value2) |
| `--auth-basic` | Basic auth (format: username:password) |
| `--auth-bearer` | Bearer token |
| `--auth-api-key` | API key (format: key_name:key_value) |
| `--var` | Variables (format: key=value) |

### Environment Management

```bash
# List environments
python main.py env list

# Create environment
python main.py env create dev API_URL=https://dev.api.com

# Switch environment
python main.py env use 1

# Show current environment
python main.py env show
```

### History & Saved Requests

```bash
# View history
python main.py history -n 20

# Clear history
python main.py history-clear

# Save a request
python main.py save --name "Get Users" --method GET --url https://api.example.com/users

# List saved requests
python main.py saved

# Load and execute saved request
python main.py load 1
```

## Project Structure

```
api_toolkit/
├── main.py          # CLI entry point
├── shell.py        # Interactive shell
├── http_client.py  # HTTP client core
├── formatter.py   # Response formatter
├── storage.py     # SQLite persistence
├── requirements.txt
└── Windows launcher
```

## Usage Examples

### Development Environment Setup

```bash
# Create development environment
python main.py env create dev API_URL=https://dev.example.com API_KEY=dev_key_123

# Create production environment
python main.py env create prod API_URL=https://api.example.com API_KEY=prod_key_456

# Switch to development environment
python main.py env use 1

# Send request (variables auto-replaced)
python main.py request GET {{API_URL}}/users --auth-bearer {{API_KEY}}
```

### RESTful API Debugging

```bash
# Get user list
python main.py request GET https://api.example.com/users -p "page=1&size=20"

# Create user
python main.py request POST https://api.example.com/users \
  -H "Content-Type:application/json" \
  -d '{"username":"test","email":"test@example.com"}'

# Update user
python main.py request PUT https://api.example.com/users/123 \
  -H "Content-Type:application/json" \
  -d '{"status":"active"}'

# Delete user
python main.py request DELETE https://api.example.com/users/123
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

- GitHub: [https://github.com/will1189/API-Toolkit](https://github.com/will1189/API-Toolkit)

## Author

- GitHub: [https://github.com/simplecoder-1](https://github.com/simplecoder-1)
- Gitee: [https://gitee.com/simplecoder-1](https://gitee.com/simplecoder-1)
