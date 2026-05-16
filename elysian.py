#!/usr/bin/env python3
"""
Elysian - A Python alternative to curl
A modern HTTP client for the command line
"""

import argparse
import sys
import json
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
import ssl

def parse_headers(headers_list):
    """Parse headers from list of strings in format 'Key: Value'"""
    headers = {}
    for header in headers_list:
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def get_filename_from_url(url):
    """Extract filename from URL"""
    parsed = urlparse(url)
    path = parsed.path
    filename = os.path.basename(path)
    if not filename or filename == '/':
        return 'index.html'
    return filename

def get_filename_from_content_disposition(headers):
    """Extract filename from Content-Disposition header"""
    content_disposition = headers.get('Content-Disposition', '')
    if 'filename=' in content_disposition:
        parts = content_disposition.split('filename=')
        if len(parts) > 1:
            filename = parts[1].strip('"\'')
            filename = filename.split(';')[0].strip()
            return filename
    return None

def format_size(size):
    """Format size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def make_request(url, method='GET', headers=None, data=None, verbose=False, insecure=False, output_file=None, show_progress=False):
    """Make HTTP request with given parameters"""
    if headers is None:
        headers = {}
    request = Request(url, data=data, headers=headers, method=method)
    
    ssl_context = ssl.create_default_context()
    if insecure:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        if verbose:
            print(f"> {method} {url}")
            for key, value in headers.items():
                print(f"> {key}: {value}")
            if data:
                print(f"> [Data length: {len(data)} bytes]")
            print(">")
        
        response = urlopen(request, context=ssl_context)
        
        if verbose:
            print(f"< HTTP/{response.version} {response.status} {response.reason}")
            for key, value in response.headers.items():
                print(f"< {key}: {value}")
            print("<")

        content_length = response.headers.get('Content-Length')
        total_size = int(content_length) if content_length else None

        if output_file:
            chunk_size = 8192
            downloaded = 0
            
            with open(output_file, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if show_progress and total_size:
                        percent = (downloaded / total_size) * 100
                        bar_length = 40
                        filled = int(bar_length * downloaded / total_size)
                        bar = '█' * filled + '-' * (bar_length - filled)
                        sys.stderr.write(f"\r[{bar}] {percent:.1f}% {format_size(downloaded)}/{format_size(total_size)}")
                        sys.stderr.flush()
                    elif show_progress:
                        sys.stderr.write(f"\rDownloaded: {format_size(downloaded)}")
                        sys.stderr.flush()
            
            if show_progress:
                sys.stderr.write("\n")
                sys.stderr.flush()
            
            return response.status, response.headers, None
        else:
            body = response.read()

            try:
                body_text = body.decode('utf-8')
            except UnicodeDecodeError:
                body_text = body.decode('latin-1')
            
            return response.status, response.headers, body_text
        
    except HTTPError as e:
        if verbose:
            print(f"< HTTP/{e.version} {e.code} {e.reason}")
            for key, value in e.headers.items():
                print(f"< {key}: {value}")
            print("<")
        
        if output_file:
            return e.code, e.headers, None
        else:
            body = e.read()
            try:
                body_text = body.decode('utf-8')
            except UnicodeDecodeError:
                body_text = body.decode('latin-1')
            
            return e.code, e.headers, body_text
        
    except URLError as e:
        print(f"Error: {e.reason}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Elysian - A Python alternative to curl',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  elysian https://example.com
  elysian -X POST https://example.com -d '{"key": "value"}'
  elysian -H "Authorization: Bearer token" https://api.example.com
  elysian -v https://example.com
  elysian -k https://self-signed.example.com
        """
    )
    
    parser.add_argument('url', help='URL to request')
    parser.add_argument('-X', '--request', default='GET',
                        help='Request method (GET, POST, PUT, DELETE, etc.)')
    parser.add_argument('-H', '--header', action='append', default=[],
                        help='Add header (can be used multiple times)')
    parser.add_argument('-d', '--data', help='Data to send in request body')
    parser.add_argument('--data-binary', help='Binary data to send (same as -d)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Make the operation more talkative')
    parser.add_argument('-k', '--insecure', action='store_true',
                        help='Allow insecure SSL connections')
    parser.add_argument('-o', '--output', help='Write output to file instead of stdout')
    parser.add_argument('-O', '--remote-name', action='store_true',
                        help='Write output to file using remote filename')
    parser.add_argument('-i', '--include', action='store_true',
                        help='Include protocol headers in the output')
    parser.add_argument('-L', '--location', action='store_true',
                        help='Follow redirects (not implemented yet)')
    parser.add_argument('--json', action='store_true',
                        help='Send data as JSON (sets Content-Type: application/json)')
    parser.add_argument('--no-progress', action='store_true',
                        help='Disable progress bar for downloads')
    
    args = parser.parse_args()

    headers = parse_headers(args.header)

    data = None
    if args.data:
        data = args.data.encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif args.data_binary:
        data = args.data_binary.encode('utf-8')
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/octet-stream'

    if args.json and args.data:
        try:
            json.loads(args.data)
            headers['Content-Type'] = 'application/json'
        except json.JSONDecodeError:
            print("Error: Invalid JSON data", file=sys.stderr)
            sys.exit(1)

    output_file = None
    if args.remote_name:
        output_file = get_filename_from_url(args.url)
    elif args.output:
        output_file = args.output

    show_progress = output_file and not args.no_progress

    status, response_headers, body = make_request(
        args.url,
        method=args.request,
        headers=headers,
        data=data,
        verbose=args.verbose,
        insecure=args.insecure,
        output_file=output_file,
        show_progress=show_progress
    )

    if args.remote_name and output_file:
        content_filename = get_filename_from_content_disposition(response_headers)
        if content_filename:
            os.rename(output_file, content_filename)
            output_file = content_filename
            if args.verbose:
                print(f"Renamed to: {content_filename}")

    if output_file:
        if args.verbose or show_progress:
            print(f"Downloaded: {output_file}")
    elif args.output:
        with open(args.output, 'w') as f:
            f.write(body)
        if args.verbose:
            print(f"Output written to {args.output}")
    else:
        if args.include and not args.verbose:
            print(f"HTTP/1.1 {status}")
            for key, value in response_headers.items():
                print(f"{key}: {value}")
            print()
        if body is not None:
            print(body, end='')

    sys.exit(status if status >= 100 and status < 600 else 0)

if __name__ == '__main__':
    main()
