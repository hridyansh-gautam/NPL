from pikepdf import Pdf

with Pdf.open('ex_xmp.pdf') as pdf:
    with pdf.open_metadata() as meta:
        print( meta['dc:title'] )
        print( ",".join( meta['dc:creator'] ) )
        


