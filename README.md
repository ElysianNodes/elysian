# Elysian

A Python alternative to curl - a modern HTTP client for the command line.

## Features

- HTTP methods: GET, POST, PUT, DELETE, etc.
- Custom headers support
- Data/body sending
- Verbose mode for debugging
- SSL/TLS support (with insecure option)
- JSON support
- Output to file

## Installation

### From GitHub

Clone the repository and run the installation script:

```bash
git clone https://github.com/ElysianNodes/elysian.git
cd elysian
sudo ./install.sh
```

This will install `elysian` to `/usr/local/bin`, making it available system-wide.

### From Local Source

If you have the source files locally, run:

```bash
sudo ./install.sh
```

## Usage

### Basic GET request

```bash
elysian https://example.com
```

### POST request with data

```bash
elysian -X POST https://example.com/api -d '{"key": "value"}'
```

### Add custom headers

```bash
elysian -H "Authorization: Bearer token" https://api.example.com
```

### Verbose mode (see request/response details)

```bash
elysian -v https://example.com
```

### Send JSON data

```bash
elysian -X POST https://api.example.com --json -d '{"name": "John"}'
```

### Ignore SSL errors (self-signed certificates)

```bash
elysian -k https://self-signed.example.com
```

### Output to file

```bash
elysian -o output.html https://example.com
```

### Download with remote filename

```bash
elysian -O https://example.com/file.zip
```

### Download without progress bar

```bash
elysian -O --no-progress https://example.com/largefile.zip
```

### Include headers in output

```bash
elysian -i https://example.com
```

## Help

```bash
elysian --help
```

## Examples

```bash
# Simple GET
elysian https://jsonplaceholder.typicode.com/posts/1

# POST with JSON
elysian -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "foo", "body": "bar", "userId": 1}'

# Multiple headers
elysian -H "Accept: application/json" \
  -H "User-Agent: Elysian/1.0" \
  https://api.example.com

# Verbose debugging
elysian -v -X POST https://httpbin.org/post -d "test=data"
```

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## License

Apache 2.0
