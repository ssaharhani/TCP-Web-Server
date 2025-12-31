from socket import *               # Import socket library for network communication
import os                         # Used to interact with the file system
from urllib.parse import urlparse, parse_qs  # Used to parse URLs and query strings

# Create the server socket using IPv4 and TCP
server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # Allow address reuse to avoid 'address already in use' error
server.bind(('localhost', 5012))                # Bind the server to localhost and port 5012
server.listen(1)                                # Start listening for incoming connections (max 1 connection in queue)
print("Server is running on port 5012")

# Function to return correct content-type header based on file extension
def what_file_type(filename):
    if filename.endswith(".html"): return "text/html"
    elif filename.endswith(".css"): return "text/css"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"): return "image/jpeg"
    elif filename.endswith(".png"): return "image/png"
    elif filename.endswith(".mp4"): return "video/mp4"
    else: return "application/octet-stream"  # Default for unknown file types

# Function to find a matching local file (image or video) by keyword and extension
def find_local_file(folder, keyword, extensions):
    if not os.path.exists(folder): return None  # Folder not found

    # Supported keyword mapping (English/Arabic keywords)
    valid_keywords = {"famine": "famine", "مجاعة": "famine",
                      "displacement": "displacement", "نزوح": "displacement"}

    trimmed = keyword.strip().lower()         # Clean input
    target = valid_keywords.get(trimmed)      # Get mapped target keyword
    if not target: return None                # If keyword is not valid, return nothing

    # Search for a matching file in folder with target keyword and supported extension
    for f in os.listdir(folder):
        if target in f.lower() and any(f.lower().endswith(ext) for ext in extensions):
            return f"{folder}/{f}"  # Return full path if match found
    return None

# Infinite loop to handle multiple client requests one at a time
while True:
    client_socket, client_address = server.accept()  # Accept client connection

    try:
        # Read full HTTP request from client
        request_data = b''
        while True:
            chunk = client_socket.recv(1024)
            request_data += chunk
            if b'\r\n\r\n' in request_data or not chunk:  # End of headers or connection closed
                break

        request_text = request_data.decode('utf-8', errors='ignore')  # Decode request safely
        lines = request_text.strip().splitlines()                    # Split into lines

        if not lines:
            client_socket.close()
            continue

        first_line = lines[0]  # Example: GET /main_en.html HTTP/1.1
        try:
            method, url_path, _ = first_line.split()  # Extract method and path
        except ValueError:
            print("Malformed request from:", client_address)
            client_socket.close()
            continue

        # Print request details for debugging
        print("\n" + "=" * 60)
        print("HTTP REQUEST DETAILS:")
        print("=" * 60)
        print(request_text.strip())
        print("=" * 60)
        print("Client wants: {} {}".format(method, url_path))

        file_to_serve = None  # Default to no file

        # Route handling
        if url_path in ['/', '/index.html', '/main_en.html', '/en']:
            file_to_serve = 'html/main_en.html'
        elif url_path in ['/ar', '/main_ar.html']:
            file_to_serve = 'html/main_ar.html'
        elif url_path.startswith('/event'):
            # Parse event query string
            parsed = urlparse(url_path)
            keyword = parse_qs(parsed.query).get('keyword', [''])[0].strip()
            type_ = parse_qs(parsed.query).get('type', ['text'])[0].lower()

            # Handle event type: text/image/video
            if type_ == "text":
                html_map = {
                    "famine": "html/famine_crisis.html", "مجاعة": "html/famine_crisis_ar.html",
                    "displacement": "html/event_displacement_en.html", "نزوح": "html/event_displacement_ar.html"
                }
                page = html_map.get(keyword, html_map.get(keyword.lower()))
                if page and os.path.exists(page):
                    location = f"http://localhost:5012/{page}"  # Serve local HTML
                else:
                    location = f"https://www.aljazeera.com/search/{keyword.replace(' ', '%20')}"  # External redirect
            elif type_ == "image":
                path = find_local_file("imgs", keyword, [".jpg", ".png", ".jpeg"])
                location = f"http://localhost:5012/{path}" if path else f"https://www.google.com/search?q={keyword.replace(' ', '+')}&udm=2"
            elif type_ == "video":
                path = find_local_file("videos", keyword, [".mp4"])
                location = f"http://localhost:5012/{path}" if path else f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}"
            else:
                location = f"https://www.google.com/search?q={keyword.replace(' ', '+')}"

            # Send 307 redirect response
            response = f"HTTP/1.1 307 Temporary Redirect\r\nLocation: {location}\r\n\r\n"
            print(f"<-- 307 Redirect to: {location}")
            client_socket.send(response.encode())
            continue  # Move to next request

        # Serve static files (HTML, CSS, images, videos)
        elif url_path.startswith(('/html/', '/css/', '/imgs/', '/videos/')):
            file_to_serve = url_path[1:]  # Strip the leading /

        else:
            print(f"<-- 404 Not Found for: {url_path}")
            raise FileNotFoundError()  # Trigger 404 page

        # If the file does not exist, raise 404 error
        if not os.path.exists(file_to_serve):
            raise FileNotFoundError()

        # Read and send file content
        with open(file_to_serve, 'rb') as f:
            content = f.read()

        # Build HTTP response header
        content_type = what_file_type(file_to_serve)
        header = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            f"Connection: close\r\n\r\n"
        )

        # Send response (header + file content)
        client_socket.sendall(header.encode() + content)

        # Print response info
        print("\nHTTP RESPONSE SENT:")
        print("Status: 200 OK")
        print("Content-Type: {}".format(content_type))
        print("Content-Length: {} bytes".format(len(content)))
        print("File served: {}".format(file_to_serve))

    # Handle 404 error response
    except FileNotFoundError:
        error_page = """<!DOCTYPE html>
<html>
<head><title>Error 404</title></head>
<body>
<p style="color: red;">The file is not found</p>
<p>Client IP: {}</p>
<p>Client Port: {}</p>
</body>
</html>""".format(client_address[0], client_address[1]).encode('utf-8')

        error_response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n\r\n"
        ).format(len(error_page))

        print("\nHTTP RESPONSE SENT:")
        print("Status: HTTP/1.1 404 Not Found")
        print("Content-Type: text/html")
        print("Error page for client:", client_address)

        client_socket.sendall(error_response.encode() + error_page)

    # Handle any other unexpected error
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        client_socket.close()  # Close connection after response
