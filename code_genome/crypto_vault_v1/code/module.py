def _derive_keystream(secret_key: str, nonce: str, size: int) -> bytes:
    seed = hashlib.sha256(f"{secret_key}:{nonce}".encode('utf-8')).digest()
    stream = bytearray()
    counter = 0
    while len(stream) < size:
        block = hashlib.sha256(seed + counter.to_bytes(4, 'big')).digest()
        stream.extend(block)
        counter += 1
    return bytes(stream[:size])

