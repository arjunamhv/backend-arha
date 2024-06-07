from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import re
import socket
import sublist3r
import subprocess

app = Flask(__name__)
CORS(app)

def decode_base64(data):
    return base64.b64decode(data).decode('utf-8')

def encode_base64(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

@app.route('/nslookup', methods=['POST'])
def nslookup_route():
    encoded_domain = request.json.get('domain')
    if not encoded_domain:
        return jsonify({'error': 'No domain provided.'}), 400

    domain = decode_base64(encoded_domain)

    try:
        result = socket.gethostbyname(domain)
        encoded_result = encode_base64(result)
        return jsonify({'result': encoded_result})
    except socket.gaierror:
        return jsonify({'error': f'The domain {domain} does not exist or could not be resolved.'})

@app.route('/subdomains', methods=['POST'])
def scan_subdomains_route():
    encoded_domain = request.json.get('domain')
    if not encoded_domain:
        return jsonify({'error': 'No domain provided.'}), 400

    domain = decode_base64(encoded_domain)

    print(f"Scanning subdomains for: {domain}")
    subdomains_list = sublist3r.main(
        domain=domain,
        threads=10,
        savefile=None,
        ports=None,
        silent=True,
        verbose=False,
        enable_bruteforce=False,
        engines=None
    )

    print("Found subdomains:")
    for subdomain in subdomains_list:
        print(subdomain)

    encoded_subdomains = [encode_base64(subdomain) for subdomain in subdomains_list]
    return jsonify({'subdomains': encoded_subdomains}), 200

def format_nmap_ports(nmap_output):
    formatted_ports = []
    lines = nmap_output.split("\n")
    capture = False

    for line in lines:
        if re.match(r"PORT\s+STATE\s+SERVICE", line):
            capture = True
            continue

        if capture:
            if line.strip() == "":
                break
            match = re.match(r"(\d+/tcp)\s+(\w+)\s+(\S+)", line)
            if match:
                port_info = {
                    "port": match.group(1),
                    "state": match.group(2),
                    "service": match.group(3)
                }
                formatted_ports.append(port_info)

    return formatted_ports

@app.route('/nmap', methods=['POST'])
def scan_nmap():
    encoded_domain = request.json.get('domain')
    
    if not encoded_domain:
        return jsonify({'error': 'No domain provided.'}), 400

    domain = decode_base64(encoded_domain)

    try:
        nmap_output = subprocess.check_output(['nmap', domain], stderr=subprocess.STDOUT)
        formatted_ports = format_nmap_ports(nmap_output.decode('utf-8'))
        encoded_result = [{'port': item['port'], 'state': item['state'], 'service': encode_base64(item['service'])} for item in formatted_ports]
        return jsonify({'result': encoded_result})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output.decode('utf-8')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/nikto', methods=['POST'])
def scan_nikto():
    encoded_domain = request.json.get('domain')

    if not encoded_domain:
        return jsonify({'error': 'Domain is required'}), 400

    domain = decode_base64(encoded_domain)

    try:
        nikto_output = subprocess.check_output(['nikto', '-h', domain], stderr=subprocess.STDOUT)
        nikto_result = nikto_output.decode('utf-8')
        encoded_nikto_result = encode_base64(nikto_result)
        return jsonify({'nikto_result': encoded_nikto_result})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': e.output.decode('utf-8')}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
