from pypdf import PdfReader

meta = PdfReader("ex_xmp.pdf").xmp_metadata 

print( meta.dc_title['x-default'] )
print( ",".join( meta.dc_creator ) )
        


