import hashlib

def generate_checksum(file_path, algorithm='sha256'):
    """
    Generate a checksum for a given file using the specified algorithm.

    :param file_path: Path to the file.
    :param algorithm: Hashing algorithm to use (default: 'sha256').
    :return: Checksum of the file.
    """
    hash_function = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read():
            hash_function.update(chunk)
    return hash_function.hexdigest()


# pdf_file = "./pdfs/N23070405_D3.03_C-037.pdf"  #filename
# checksum_file = "./checksums/N23070405_D3.03_C-037.txt"
# actual_checksum = read_file(checksum_file)
# current_checksum=generate_checksum(pdf_file)
# # Verify the checksum
# print(actual_checksum==current_checksum)
