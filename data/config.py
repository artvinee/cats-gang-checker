API_ID =  0
API_HASH = ''


DELAYS = {
    'ACCOUNT': [1, 4],  # delay between connections to accounts (the more accounts, the longer the delay)
    'REPEAT': [1, 2],
    'MAX_ATTEMPTS': 5
}

PROXY = {
    "USE_PROXY_FROM_FILE": False,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "data/proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": "socks5",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": "socks5"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
        }
}

REF_CODE = "ew-KHGT-G4LUSSZVy2a9v"

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

SOFT_INFO = "CatsGang soft by https://t.me/artvinee"
