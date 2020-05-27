import sys
from toyotama.util.log import * 

# |chosen_pt|FLAG|pad|
def ecb_chosen_plaintext_attack(encrypt_oracle, plaintext_space=b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_', known_plaintext=b'', block_size=16, verbose=False):
    from random import sample
    block_end = block_size * (len(known_plaintext)//(block_size-2) + 1)
    for _ in range(1, 100):

        # shuffle plaintext_space to reduce complexity
        plaintext_space = bytes(sample(bytearray(plaintext_space), len(plaintext_space)))

        # get the encrypted block which includes the beginning of FLAG
        if verbose:
            info('Getting the encrypted block which includes the beginning of FLAG')

        if len(known_plaintext) % block_size == block_size-1:
            block_end += block_size

        
        chosen_plaintext = b'\x00'*(block_end-len(known_plaintext)-1) 
        print(chosen_plaintext)
        encrypted_block = encrypt_oracle(chosen_plaintext)
        encrypted_block = encrypted_block[block_end-block_size:block_end]


        # bruteforcing all of the characters in plaintext_space 
        if verbose:
            info('Bruteforcing all of the characters in plaintext_space')
        for c in plaintext_space:
            if verbose:
                sys.stderr.write(f'\r{colorify(Color.GREY, known_plaintext[:-1].decode())}{colorify(Color.RED, known_plaintext[-1:].decode())}{colorify(Color.MAGENTA, chr(c))}')
            payload = b'\x00'*(block_end-len(known_plaintext)-1) + known_plaintext + bytearray([c])
            enc_block = encrypt_oracle(payload)[block_end-block_size:block_end]
            if encrypted_block == enc_block:
                known_plaintext += bytearray([c])
                if verbose:
                    sys.stderr.write('\n')
                break



# [str,b64encoded] plaintext >> padding_oracle >> [bool] padding is valid?
def padding_oracle_attack(ciphertext, padding_oracle, iv=b'', block_size=16, verbose=False):
    from base64 import b64encode
    cipher_block = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    cipher_block.reverse()
    plaintext = b''

    def is_valid(c_target, d_prev, nth_byte, i):
        attempt_byte = bytes.fromhex(f'{i:02x}')
        adjusted_bytes = bytes(c^nth_byte for c in d_prev)

        payload = b'\x00'*(block_size-nth_byte) + attempt_byte + adjusted_bytes + c_target
        if verbose:
            sys.stdout.write('\033[2K\033[G'
                    +colorify(Color.GREY, repr(b'\x00'*(block_size-nth_byte))[2:-1]) 
                    +colorify(Color.RED, repr(attempt_byte)[2:-1])
                    +colorify(Color.MAGENTA, repr(adjusted_bytes)[2:-1])
                    +colorify(Color.DARK_GREY, repr(c_target)[2:-1])
            )
            sys.stdout.flush()

        payload = b64encode(payload).decode()
        return padding_oracle(payload)


    for _ in range(len(cipher_block)-1):
        c_target, c_prev = cipher_block[:2]
        print(cipher_block)
        cipher_block.pop(0)
        nth_byte = 1
        i = 0
        m = d_prev = b''
        while True:
            if is_valid(c_target, d_prev, nth_byte, i):
                m += bytes.fromhex(f'{i^nth_byte^c_prev[-nth_byte]:02x}')
                d_prev = bytes.fromhex(f'{i^nth_byte:02x}')+d_prev
                nth_byte += 1
                i = 0
                if nth_byte <= block_size:
                    continue
                break
            i += 1
            if i > 0xff:
                error('Not Found')
                return None
        plaintext = m[::-1] + plaintext 

        if verbose:
            print()
            info(f'Decrypt(c{len(cipher_block)}): {repr(d_prev)[2:-1]}')
            info(f'm{len(cipher_block)}: {repr(m[::-1])[2:-1]}')
            info(f'plaintext: {repr(plaintext)[2:-1]}')

    return plaintext


