import socket                       
import threading              
import time                           
import os                             
import random                     
import base64                         
from urllib.parse import urlparse    

# Configuration settings for the proxy server
HOST = '127.0.0.1'                   
PORT = 8080                           
DELAY = 1.0                         
CHUNK_SIZE = 4096                  
MEME_FOLDER = "./memes"               # The folder path where memes are stored
EASTER_EGG_URL = "google.ca"          #URL that will trigger the Easter Egg task

def get_random_meme():
    #List all files in the MEME_FOLDER that end with common image file extensions
    meme_files = [f for f in os.listdir(MEME_FOLDER) if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
    #Return the path of a random meme file if available or otherwise return None
    return os.path.join(MEME_FOLDER, random.choice(meme_files)) if meme_files else None

def send_error_response(client_socket, status_code=500, message="Internal Server Error"):
    #Gives a HTTP error message with a status code
    response = (
        f"HTTP/1.1 {status_code} {message}\r\n"  
        "Content-Type: text/html\r\n"            
        "Connection: close\r\n\r\n"               
        f"<html><body><h1>{status_code} - {message}</h1></body></html>"  #HTML body with error messgae  and status code
    ).encode()  
    try:
        client_socket.send(response)  #send error response to the client
    except Exception:
        pass                          #If tehre is an error that happens while sending it ignore it
    client_socket.close()             #close the client socket

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096)  #This is the clients request
        if not request:
            send_error_response(client_socket, 400, "Bad Request")  #If there is no data being received send a 400 error, bad request
            return

        #parse the first line of the clients request
        first_line = request.split(b'\r\n')[0]
        parts = first_line.split(b' ')
        if len(parts) < 2:
            send_error_response(client_socket, 400, "Bad Request")  #Send a 400 error if incomplete
            return
        #Get its method
        method = parts[0].decode('utf-8').upper()

        #The method is CONNECT
        if method == "CONNECT":
            #find its host and port from its request
            host_port = parts[1].decode('utf-8')
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                port = int(port)
            else:
                host = host_port
                port = 443 
            try:
                remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote_socket.connect((host, port))
                client_socket.send(b"HTTP/1.1 200 Connection established\r\n\r\n")
            except Exception:
                #if connection fails send 502 error message bad gateway
                send_error_response(client_socket, 502, "Bad Gateway")
                return

            #Function to pass data between client and server
            def forward(source, destination):
                try:
                    while True:
                        data = source.recv(CHUNK_SIZE)
                        if not data:
                            break
                        destination.sendall(data)
                except Exception:
                    pass
                finally:
                    destination.close()
                    source.close()

            #Starts two threads to forward data both ways.
            t1 = threading.Thread(target=forward, args=(client_socket, remote_socket))
            t2 = threading.Thread(target=forward, args=(remote_socket, client_socket))
            t1.start()
            t2.start()
            return 

        #For HTTP requests
        url = parts[1]
        parsed_url = urlparse(url.decode('utf-8'))
        if not parsed_url.hostname:
            send_error_response(client_socket, 400, "Invalid URL")
            return

        #Finds the hostname and path from a URL
        host = parsed_url.hostname
        path = parsed_url.path if parsed_url.path else "/"
        if parsed_url.query:
            path += "?" + parsed_url.query  
        port = parsed_url.port if parsed_url.port else 80

        #Easter Egg feature if user geos to the easter egg URL
        if EASTER_EGG_URL in host:
            meme_path = get_random_meme()  #Get some random meme from the memes folder
            if meme_path:
                with open(meme_path, "rb") as meme_file:
                    meme_data = base64.b64encode(meme_file.read()).decode('utf-8')
                    #A small HTML page that has a meme image embedded
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/html\r\n"
                        "Connection: close\r\n\r\n"
                        "<html><head><title>Easter Egg</title></head>"
                        "<body style='text-align:center; background-color:#000; color:#fff;'>"
                        "<h1>You've Found the Easter Egg!</h1>"
                        f"<img src='data:image/jpeg;base64,{meme_data}' width='500'><br>"
                        "</body></html>"
                    ).encode()  
                    client_socket.send(response)  #Send the Easter Egg response to the client
                    client_socket.close()          
                    return                     

        #Http requests
        try:
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Socket that connects to the remote serveer
            remote_socket.connect((host, port))  #Connect to the server using the host and port
            remote_socket.sendall(request)       
        except Exception:
            send_error_response(client_socket, 502, "Bad Gateway")  #If it does not connect send a 502 bad gateway messgae
            return

        response_headers = b""
        body = b""
        image_requested = False 

        while True:
            response_chunk = remote_socket.recv(CHUNK_SIZE)  #Gets a chunk of data from remote server
            if not response_chunk:
                break                                      #break if there is no more data being received
            response_headers += response_chunk             
            if b'\r\n\r\n' in response_headers:             
                header_end = response_headers.find(b'\r\n\r\n') + 4  
                body = response_headers[header_end:]        
                response_headers = response_headers[:header_end]  
                if b'Content-Type: image/' in response_headers:  #Checks and sees if its for an image
                    image_requested = True                  #Sets flag if its a image
                break                                      

        #Replaces 50% of images with a meme
        if image_requested and random.random() < 0.5:
            meme_path = get_random_meme() 
            if meme_path:
                try:
                    with open(meme_path, "rb") as meme_file:  #Opens the memes file
                        meme_data = meme_file.read()          #Read the memes data
                    #MAkes a new HTTP header for the memes image 
                    header = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: image/jpeg\r\n"
                        "Content-Length: " + str(len(meme_data)) + "\r\n"
                        "Connection: close\r\n\r\n"
                    ).encode()
                    client_socket.send(header)  #Send header to client
                    client_socket.send(meme_data)  #Send the meme image to client
                    remote_socket.close()         
                    client_socket.close()         
                    return                    
                except Exception:
                    #If meme is not replaced and fails output the original image
                    pass

        # Send the original response headers and the initial body (if any) to the client
        client_socket.send(response_headers + body)
        # Continue to forward any remaining data from the remote server to the client
        while True:
            response_chunk = remote_socket.recv(CHUNK_SIZE)
            if not response_chunk:
                break                        
            client_socket.sendall(response_chunk) 

        remote_socket.close()  
        client_socket.close() 

    except Exception as e:
        print("Error handling client:", e)  #print error message if problem with the client
        send_error_response(client_socket, 500, "Internal Server Error")  #Sends a 500 error messsage Internal Server Error 
        client_socket.close()  

def start_proxy():
    #Prints a message showing that the proxy is running and showing its dealay and chunk size
    print(f"Meme Proxy running on {HOST}:{PORT}, with a delay of {DELAY} seconds per {CHUNK_SIZE} bytes.")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    server_socket.bind((HOST, PORT))             
    server_socket.listen(5)                     
    while True:
        client_socket, addr = server_socket.accept()  
        print(f"Connection from {addr}")         
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))  
        client_handler.start()                     

#Starts the proxy server
if __name__ == "__main__":
    start_proxy()  