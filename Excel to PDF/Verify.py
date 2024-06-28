import hashlib

def generate_checksum(filename):
  # Open the file in binary read mode
  with open(filename, 'rb') as file:
    # Create a SHA-256 hash object
    hasher = hashlib.sha256()
    # Read the file content in chunks and update the hash
    for chunk in iter(lambda: file.read(), b''):
      hasher.update(chunk)
    # Return the checksum in hexadecimal format
    return hasher.hexdigest()

def read_file(filename):
    with open(filename,"r") as file:
        read_content=file.read()
        return read_content

if __name__ == '__main__':
    pdf_file = "./pdfs/N23070405_D3.03_C-037.pdf"  #filename
    checksum_file = "./checksums/N23070405_D3.03_C-037.txt"
    actual_checksum = read_file(checksum_file)
    current_checksum=generate_checksum(pdf_file)
    # Verify the checksum
    print(actual_checksum==current_checksum)
