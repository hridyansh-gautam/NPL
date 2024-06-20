from flask import Flask, request, jsonify
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

checksums = {
    '62cdb7020ff920e5aa642c3d4066950dd1f01f4d18ef927cfb523c4982f1b240',
    'd014d80bacc6b7e1ef4cc93fe45b31e74a107a296635f91cf2aebc8a586c4280',
    'b6e7ee0900d39c8a79b9cc1d512d93ebddb16c690e605f75851ea7e268fcbff5',
    '00e3e5af2b1eb28cc998fc187cd6c5b146e5d7d62c7dc960a8b2df2a2c3eb0b3',
    'f98ce315a9f91f82f39befe40f0278128a68db6b78856b3c283dcbe34811b7fd',
    '71d7ea22b4f72a3850f7a2c8c76d9f7ec53482e8a69494a5e35b5e13406c6803',
    'ff26de0543feccde8c7ca66311846f33c29df95b2476e337b047b21f25b5fd85',
    'daed81f29ce32d487d3dd2b4c54d2e1a39c45846083de129640c9a45f4c95f6b',
    'e35cb47c2b992ed2b3e16a535179db1c763ac4dc16b8477db97a2fe82eeef6db',
    '6b2d2a9ab37b4e18859e5e03d922f6cefded92a85d7b01d800eaa9c41864cc90'
}

@app.route('/verify/<checksum>', methods=['GET'])
def verify_checksum(checksum):
    if checksum in checksums:
        return jsonify({'valid': True})
    else:
        return jsonify({'valid': False})

if __name__ == '__main__':
    port = 8080
    try:
        with WSGIServer(('0.0.0.0', port), app) as server:
            print(f'Server running at http://localhost:{port}')
            print('Press CTRL+C to quit')
            server.serve_forever()
    except KeyboardInterrupt:
        pass