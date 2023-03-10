from libretranslate.storage import get_storage

active = False
threshold = -1

def forgive_banned():
    global threshold

    clear_list = []
    s = get_storage()
    banned = s.get_all_hash_int("banned")

    for ip in banned:
        if banned[ip] <= 0:
            clear_list.append(ip)
        else:
            s.set_hash_int("banned", ip, min(threshold, banned[ip]) - 1)

    for ip in clear_list:
        s.del_hash("banned", ip)

def setup(args):
    global active
    global threshold

    if args.req_flood_threshold > 0:
        active = True
        threshold = args.req_flood_threshold

def report(request_ip):
    if active:
        get_storage().inc_hash_int("banned", request_ip)

def decrease(request_ip):
    s = get_storage()
    if s.get_hash_int("banned", request_ip) > 0:
        s.dec_hash_int("banned", request_ip)

def has_violation(request_ip):
    s = get_storage()
    return s.get_hash_int("banned", request_ip) > 0

def is_banned(request_ip):
    s = get_storage()

    # More than X offences?
    return active and s.get_hash_int("banned", request_ip) >= threshold
