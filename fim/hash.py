import hashlib

def compute_hash(path, algorithm="sha256", block_size=65536):
    h = hashlib.new(algorithm)
    
    with open(path, "rb") as f:
        while True:
            chunk = f.read(block_size)
            
            if not chunk:
                break
            h.update(chunk)
    
    return h.hexdigest()
