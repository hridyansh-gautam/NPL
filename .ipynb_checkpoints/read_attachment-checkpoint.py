# Use this script to read the text file 
# embedded in ex.pdf in the minimal example.
#
from pypdf import PdfReader

attached = PdfReader("ex.pdf").attachments  

if len(attached) != 1:
    raise RuntimeError("Expect a single attachment")

for file_name, content_list in attached.items():

    # Elements in content_list are Python byte-literals
    # Here we convert the bytes to a string.
    content_as_str = content_list[0].decode('utf-8')
    
    print(f"\nThe {file_name} file contents are:\t{content_as_str!r}")
