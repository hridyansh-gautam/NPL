from flask import Flask
from gevent.pywsgi import WSGIServer
import random
import string

def generate_random_string(length=10):
    hex_chars = string.hexdigits.lower()
    return ''.join(random.choice(hex_chars) for i in range(length))

port = 8080
app = Flask(__name__)

checksums = set()

@app.route('/verify/<checksum>')
def verify(checksum):
    return str(checksum in checksums)

def write_file(filename, content):
    with open(filename, "w") as file:
        file.write(content)

def append_file(filename, content):
    with open(filename, "a") as file:
        file.write(content + "\n")

def read_file(filename):
    with open(filename, "r") as file:
        read_content = file.read()
        words = read_content.split()
    return words

if __name__ == '__main__':
    c = generate_random_string()
    write_file("checksum.txt", c)
    append_file("All_checksums.txt", c)
    checksums.update(read_file("checksum.txt"))
    print(checksums)

    try:
        with WSGIServer(('0.0.0.0', port), app) as server:
            print(f'Server running at http://localhost:{port}/verify/{c}')
            print('Press CTRL+C to quit')
            server.serve_forever()
    except KeyboardInterrupt:
        pass