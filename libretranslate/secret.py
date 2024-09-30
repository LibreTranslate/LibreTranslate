import base64
import random
import string
from functools import lru_cache

from libretranslate.storage import get_storage


def to_base(n, b):
    if n == 0:
        return 0
    if n < 0:
        sign = -1
    else:
        sign = 1
    
    n *= sign
    digits = []
    while n:
        digits.append(str(n % b))
        n //= b
    return int(''.join(digits[::-1])) * sign

@lru_cache(maxsize=4)
def obfuscate(input_str):
    encoded = [ord(ch) for ch in input_str]
    ops = ['+', '-', '*', '']
    parts = []

    for c in encoded:
        num = random.randint(1, 100)
        op = random.choice(ops)
        if op == '+':
            v = c + num
            op = '-'
        elif op == '-':
            v = c - num
            op = '+'
            if random.randint(0, 1) == 0:
                op = '+false+'
        elif op == '*':
            v = c * num
            op = '/'
            if random.randint(0, 1) == 0:
                op = '/**\\/*//'

        use_dec = random.randint(0, 1) == 0
        base = random.randint(4, 7)

        if op == '':
            if use_dec:
                parts.append(f'_({c})')
            else:
                parts.append(f'_(p({to_base(c, base)},{base}))')
        else:
            if use_dec:
                parts.append(f'_({v}{op}{num})')
            else:
                parts.append(f'_(p({to_base(v, base)},{base}){op}p({to_base(num,base)},{hex(base)}))')

    for i in range(int(len(encoded) / 3)):
        c = random.randint(1, 100)
        parts.insert(random.randint(0, len(parts)), f"_(/*_({c})*/)")
    for i in range(int(len(encoded) / 3)):
        parts.insert(random.randint(0, len(parts)), f"\n[]\n")
    
    code = '(_=String.fromCharCode,p=parseInt,' + '+'.join(parts) + ')'
    return code

def generate_secret():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def rotate_secrets():
    s = get_storage()
    secret_1 = s.get_str("secret_1")
    s.set_str("secret_0", secret_1)
    s.set_str("secret_1", generate_secret())

def secret_match(secret):
    s = get_storage()
    return secret == s.get_str("secret_0") or secret == s.get_str("secret_1")

def secret_bogus_match(secret):
    if random.randint(0, 1) == 0:
        return secret == get_bogus_secret()
    return False

def get_current_secret():
    return get_storage().get_str("secret_1")

def get_current_secret_b64():
    return base64.b64encode(get_current_secret().encode("utf-8")).decode("utf-8")

def get_current_secret_js():
    return obfuscate(get_current_secret_b64())

def get_bogus_secret():
    return get_storage().get_str("secret_bogus")

def get_bogus_secret_b64():
    return base64.b64encode(get_bogus_secret().encode("utf-8")).decode("utf-8")

def get_bogus_secret_js():
    return obfuscate(get_bogus_secret_b64())

@lru_cache(maxsize=1)
def get_emoji():
    return random.choice(["😂", "🤪", "😜", "🤣", "😹", "🐒", "🙈", "🤡", "🥸", "😆", "🥴", "🐸", "🐤", "🐒🙊", "👀", "💩", "🤯", "😛", "🤥", "👻"])

def setup(args):
    if args.api_keys and args.require_api_key_secret:
        s = get_storage()

        if not s.exists("secret_0"):
            s.set_str("secret_0", generate_secret())

        if not s.exists("secret_1"):
            s.set_str("secret_1", generate_secret())

        if not s.exists("secret_bogus"):
            s.set_str("secret_bogus", generate_secret())
