import hashlib

checksums=set()

def generate_checksum(filename):
  # Open the file in binary read mode
  with open(filename, 'rb') as file:
    # Create a SHA-256 hash object
    hasher = hashlib.sha256()
    # Read the file content in chunks and update the hash
    for chunk in iter(lambda: file.read(4096), b''):
      hasher.update(chunk)
    # Return the checksum in hexadecimal format
    return hasher.hexdigest()

def write_file(filename,content):
    with open(filename,"w") as file:
        file.write(content)

def append_file(filename,content):
    with open(filename,"a") as file:
        file.write(content + "\n")

def read_file(filename):
    with open(filename,"r") as file:
            read_content=file.read()
            words = read_content.split()
    return words

def verify(filename, expected_checksum):
  actual_checksum = generate_checksum(filename)
  return actual_checksum == expected_checksum

if __name__ == '__main__':
    filename = "001.pdf"  #filename

    expected_checksum = generate_checksum(filename)
    write_file("checksum.txt",expected_checksum)

    if(expected_checksum not in read_file("All_checksums.txt") and verify(filename,expected_checksum)):
        append_file("All_checksums.txt", expected_checksum)
    else:
        print("Checksum already present")
    checksums.update(read_file("All_checksums.txt"))
    print(checksums)
    print(f"Generated checksum for {filename}: {expected_checksum}")

    # Verify the checksum
    verification_result = verify(filename, expected_checksum)
    print(f"Checksum verification for {filename}: {verification_result}")
