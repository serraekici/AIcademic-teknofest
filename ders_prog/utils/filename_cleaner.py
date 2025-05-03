import unicodedata
import re

def normalize_filename(name):
    nfkd = unicodedata.normalize('NFKD', name)
    ascii_name = nfkd.encode('ASCII', 'ignore').decode()
    ascii_name = re.sub(r'[^\w_.-]', '_', ascii_name)
    return ascii_name
