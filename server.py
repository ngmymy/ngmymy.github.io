from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib #Only for parse.unquote and parse.unquote_plus.
import json
import base64
from typing import Union, Optional
import re
# If you need to add anything above here you should check with course staff first.
contacts = []
next_id = 0
sale_text = ""
sale_active = False

def gen_table(contacts):
    str = ""
    for appt in contacts:
        str += "<tr id=" + appt.get('id') + ">"
        for attr in appt:
            if(attr == 'email'):
                str += "<td>" + "<a href=\"mailto:" + appt.get('email') + "\">" + appt.get(attr) + "</a>" + "</td>"
            
            elif(attr == 'scholarship'):
                if appt.get('scholarship') == '20000':
                    str += "<td>Tuition Fees</td>"
                elif appt.get('scholarship') == '10000':
                    str += "<td>Housing</td>"
                elif appt.get('scholarship') == '5000':
                    str += "<td>Health Insurance</td>"
                elif appt.get('scholarship') == '2000':
                    str += "<td>Technologies</td>"
                elif appt.get('scholarship') == '1000':
                    str += "<td>Textbooks</td>"
                elif appt.get('scholarship') == '3000':
                    str += "<td>Meal Plans</td>"
                elif appt.get('scholarship') == '700':
                    str += "<td>Transportation</td>"

            elif(attr == 'date'):
                str += "<td class=\"date-cell\">" + appt.get(attr) + "</td>"

            elif(attr == 'name'):
                str += "<td>" + appt.get(attr) + "</td>"

        # countdown timer        
        str += "<td id=\"time-until-cell\"></td>"

        if(appt.get('subscribe') == 'Yes'):
            str += "<td>Yes</td>"
        else: str += "<td>No</td>"
        
        str += "<td><input type=\"button\" value=\"Delete\" id=\"deleteBtn\" onclick=\"deleteRow(this)\"></td>"
        str += "</tr>"
    return str

# function for generating the contact log page html
def genConLog():
    return (
     """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" type="text/css" href="/main.css">
        <link rel="stylesheet" type="text/css" href="/main.dark.css">
        <title>Testimonies</title>
    </head>
    <body>
        <script src="/js/admin-sale.js"></script>
        <nav>
            <ul class="navs">
                <li class="nav-item"><a href="/main">Home</a></li>
                <li class="nav-item"><a href="/testimonies">Testimonies</a></li>
                <li class="nav-item"><a href="/contact">Schedule a Meeting</a></li>
                <li class="nav-item"><a href="/admin/contactlog">Appointments</a></li>
                <li class="nav-item" id="toggle-dark">
                    <div class="moon"></div>
                </li>
            </ul>
        </nav> 
        <div class="admin-sale-form">
            <label class="admin-banner">Set Sale Banner: </label>
            <input type="text" id="sale-message-input" placeholder="Enter message" maxlength="110">
            <button id="set-sale-button">Set</button>
            <button id="delete-sale-button">Delete</button>
        </div>
        <h1>Appointments Log</h1>
            <table id="contacts_table">
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Topic</th>
                    <th>Date</th>
                    <th>Time until Appointment</th>
                    <th>Subscribed</th>
                    <th>Delete Row</th>
                </tr> """ +
        gen_table(contacts) +
     """
            </table>
        <script src="/js/main.js"></script>
        <script src="/js/table.js"></script>
    </body>
    </html>
    """)

def formDataPassed ():
    return (
     """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" type="text/css" href="/main.css">
        <link rel="stylesheet" type="text/css" href="/main.dark.css">
        <title>Testimonies</title>
    </head>
    <body>
        <nav>
            <ul class="navs">
                <li class="nav-item"><a href="/main">Home</a></li>
                <li class="nav-item"><a href="/testimonies">Testimonies</a></li>
                <li class="nav-item"><a href="/contact">Schedule a Meeting</a></li>
                <li class="nav-item"><a href="/admin/contactlog">Appointments</a></li>
                <li class="nav-item" id="toggle-dark">
                    <div class="moon"></div>
                </li>
            </ul>
        </nav>
        <h1>Form Submitted</h1>
            <p>Hooray!</p>
        <script src="/js/main.js"></script>
    </body>
    </html>
    """)

def formFailed ():
    return (
     """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" type="text/css" href="/main.css">
        <link rel="stylesheet" type="text/css" href="/main.dark.css">
        <title>Testimonies</title>
    </head>
    <body>
        <nav>
            <ul class="navs">
                <li class="nav-item"><a href="/main">Home</a></li>
                <li class="nav-item"><a href="/testimonies">Testimonies</a></li>
                <li class="nav-item"><a href="/contact">Schedule a Meeting</a></li>
                <li class="nav-item"><a href="/admin/contactlog">Appointments</a></li>
                <li class="nav-item" id="toggle-dark">
                    <div class="moon"></div>
                </li>
            </ul>
        </nav>
        <h1>Submission Failed</h1>
            <p>Uh oh! Missing Required Content</p>
        <script src="/js/main.js"></script>
    </body>
    </html>
    """)

# correct login
correct_username = "admin"
correct_password = "password"

def encode(auth):
    # splits into ['Basic ','username:password'] and keeps idx 1
    encoded_credentials = auth.split('Basic ')[1]
    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
    username, password = decoded_credentials.split(":")
    return (username == correct_username and password == correct_password)

# The method signature is a bit "hairy", but don't stress it -- just check the documentation below.
def server(method: str, url: str, body: Optional[str], headers: dict[str, str]) -> tuple[Union[str, bytes], int, dict[str, str]]:    
    """
    method will be the HTTP method used, for our server that's GET, POST, DELETE
    url is the partial url, just like seen in previous assignments
    body will either be the python special None (if the body wouldn't be sent)
         or the body will be a string-parsed version of what data was sent.
    headers will be a python dictionary containing all sent headers.

    This function returns 3 things:
    The response body (a string containing text, or binary data)
    The response code (200 = ok, 404=not found, etc.)
    A _dictionary_ of headers. This should always contain Content-Type as seen in the example below.
    """
    global contacts
    global next_id
    global sale_text
    global sale_active
                
    def prompt():
        auth_header = headers.get("Authorization")
        if auth_header is None:
            return "Authentication required", 401, {"Content-Type": "text/html", "WWW-Authenticate": 'Basic realm="User Visible Realm"'}
        else:
            if encode(auth_header):
                return
            else: 
                return "Forbidden", 403, {"Content-Type": "text/html; charset=utf-8"}
        
    copy_url = url
    if "/" in url:
        copy_url = url[url.index("/"):] # preserves the path and everything that comes after the first forward slash in the URL.
        # default page

    if "?" in url:
        copy_url = copy_url[:copy_url.index("?")]

    if method == "GET":
        if copy_url == "/main" or copy_url == "/":
            return open("static/html/mainpage.html").read(), 200, {"Content-Type": "text/html"}
    
        elif copy_url == "/images/main":
            return open("static/images/scottstots.jpg", "rb").read(), 200, {"Content-Type": "image/jpeg"}

        elif copy_url == "/contact": # contact page
            return open("static/html/contactform.html").read(), 200, {"Content-Type": "text/html"}
    
        elif copy_url == "/admin/contactlog" or copy_url == "/admin":
            # password lock
            response = prompt()
            if response:
                return response
            
            return genConLog(), 200, {"Content-Type": "text/html; chatset=utf-8"}
                
        elif copy_url == "/testimonies":
            return open("static/html/testimonies.html").read(), 200, {"Content-Type": "text/html"}
    
        elif copy_url == "/main.css":
            return open("static/css/main.css", "rb").read(), 200, {"Content-Type": "text/css"}
        
        elif copy_url == "/main.dark.css":
            return open("static/css/main.dark.css", "rb").read(), 200, {"Content-Type": "text/css"}
    
        elif copy_url == "/js/table.js":
            return open("static/js/table.js").read(), 200, {"Content-Type": "text/javascript"}
    
        elif copy_url == "/js/contact.js":
            return open("static/js/contact.js").read(), 200, {"Content-Type": "text/javascript"}
    
        elif copy_url == "/js/main.js":
            return open("static/js/main.js").read(), 200, {"Content-Type": "text/javascript"}

        elif copy_url == "/js/saleBanner.js":
            return open("static/js/saleBanner.js").read(), 200, {"Content-Type": "text/javascript"}
        
        elif copy_url == "/js/admin-sale.js":
            return open("static/js/admin-sale.js").read(), 200, {"Content-Type": "text/javascript"}
        
        elif copy_url == "/api/sale":
            sale_info = {}
            if sale_active:
                sale_info["active"] = sale_active
                sale_info["message"] = sale_text

        # provides a method to convert Python objects into their JSON string representation
            return json.dumps(sale_info), 200, {"Content-Type": "application/json"}
        else: return open("static/html/404.html").read(), 404, {"Content-Type": "text/html"}
    elif method == "POST":
        if copy_url == "/contact":
            if "name" in body and "email" in body and "date" in body:
                try:
                    appointment = {}
                    parameters = body.split("&")

                    next_id += 1
                    appointment['id'] = str(next_id)

                    for items in parameters:
                        idx= items.find("=")
                
                        key= items[0:idx]
                        val = items[idx+1:len(items)]
                        appointment[key] = urllib.parse.unquote_plus(val)

                    for items in appointment:
                        if appointment.get(items) == '' or appointment.get(items) == '0':
                            return formFailed(), 400, {"Content-Type": "text/html; charset=utf-8"}
                        
                    contacts.append(appointment)
                    return formDataPassed(), 201, {"Content-Type": "text/html; charset=utf-8"}
                except:
                    # Return a 400 Bad Request if the data cannot be parsed
                    return 'bad request: invalid data in the request body', 400, {"Content-Type": "text/html; charset=utf-8"}
            else: return 'bad request: invalid data in the request body', 400, {"Content-Type": "text/html; charset=utf-8"}
        elif copy_url == "/api/sale":
            # password lock
            response = prompt()
            if response:
                return response
            
            try:
                data = json.loads(body)
                if "message" not in data:
                    return "Missing message in the request data", 400, {"Content-Type": "text/plain"}
                
                sale_text = data["message"]
                sale_active = True

                return "Sale created or updated successfully", 201, {"Content-Type": "text/plain"}
            
            except:
                return 'body not json', 400, {"Content-Type": "text/plain"}

        else: return open("static/html/404.html").read(), 404, {"Content-Type": "text/html"}
    elif method == "DELETE":
        if copy_url == "/api/contact":
        
            # password lock
            response = prompt()
            if response:
                return response
            
            #   If sent data which does not include request-header "Content-Type" 
            #   or does not have Content-Type "application/json" 
            #   or contains a body element that is not valid json  
            if not headers.get("Content-Type") == "application/json":
                return 'body not json', 400, {"Content-Type": "text/plain"}
            else:
                try:
                # parse the JSON data from the request body
                    body = json.loads(body)

                # ensure the request contains an "id" property
                    if "id" not in body:
                        return "Missing 'id' in the request data", 400, {"Content-Type": "text/plain"}
                    else:
                        for appt in contacts:
                            if appt.get("id") == body["id"]:
                                contacts.remove(appt)
                                break
                # return a success response
                    return "Contact deleted successfully", 200, {"Content-Type": "text/plain"}

                except:
                    return 'body not json', 400, {"Content-Type":"text/plain"}
        elif copy_url == "/api/sale":
            # password lock
            response = prompt()
            if response:
                return response
            
            sale_active = False
            sale_text = ""
            return "Sale deleted successfully", 200, {"Content-Type": "text/plain"}
        
        else: return open("static/html/404.html").read(), 404, {"Content-Type": "text/html"}
    else:
        # handle other URLs or return a 404 error
        return open("static/html/404.html").read(), 404, {"Content-Type": "text/html"}


# You shouldn't need to change content below this. It would be best if you just left it alone.


class RequestHandler(BaseHTTPRequestHandler):
    def c_read_body(self):
        # Read the content-length header sent by the BROWSER
        content_length = int(self.headers.get("Content-Length", 0))
        # read the data being uploaded by the BROWSER
        body = self.rfile.read(content_length)
        # we're making some assumptions here -- but decode to a string.
        body = str(body, encoding="utf-8")
        return body

    def c_send_response(self, message, response_code, headers):
        # Convert the return value into a byte string for network transmission
        if type(message) == str:
            message = bytes(message, "utf8")
        
        # Send the first line of response.
        self.protocol_version = "HTTP/1.1"
        self.send_response(response_code)
        
        # Send headers (plus a few we'll handle for you)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", len(message))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        # Send the file.
        self.wfile.write(message)
        

    def do_POST(self):
        # Step 1: read the last bit of the request
        try:
            body = self.c_read_body()
        except Exception as error:
            # Can't read it -- that's the client's fault 400
            self.c_send_response("Couldn't read body as text", 400, {'Content-Type':"text/plain"})
            raise
                
        try:
            # Step 2: handle it.
            message, response_code, headers = server("POST", self.path, body, self.headers)
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response("The server function crashed.", 500, {'Content-Type':"text/plain"})
            raise
        

    def do_GET(self):
        try:
            # Step 1: handle it.
            message, response_code, headers = server("GET", self.path, None, self.headers)
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response("The server function crashed.", 500, {'Content-Type':"text/plain"})
            raise

    def do_DELETE(self):
        # Step 1: read the last bit of the request
        try:
            body = self.c_read_body()
        except Exception as error:
            # Can't read it -- that's the client's fault 400
            self.c_send_response("Couldn't read body as text", 400, {'Content-Type':"text/plain"})
            raise
        
        try:
            # Step 2: handle it.
            message, response_code, headers = server("DELETE", self.path, body, self.headers)
            # Step 3: send the response
            self.c_send_response(message, response_code, headers)
        except Exception as error:
            # If your code crashes -- that's our fault 500
            self.c_send_response("The server function crashed.", 500, {'Content-Type':"text/plain"})
            raise

def run():
    PORT = 4131
    print(f"Starting server http://localhost:{PORT}/")
    server = ("", PORT)
    httpd = HTTPServer(server, RequestHandler)
    httpd.serve_forever()


run()
