import requests
import pickle
import steam.webauth as wa

def valid_steam_key(key):
    if not isinstance(key, str):
        return False
    key_parts = key.split("-")
    return (
        len(key) == 17
        and len(key_parts) == 3
        and all([len(part) == 5 for part in key_parts])
    )

def verify_logins_session(session):
    loggedin = []
    for url in "https://store.steampowered.com/account/registerkey":
        r = session.get(url, allow_redirects=False)
        loggedin.append(r.status_code != 301 and r.status_code != 302)
    return loggedin

def try_recover_cookies(cookie_file, session):
    try:
        with open(cookie_file, "rb") as file:
            session.cookies.update(pickle.load(file))
        return True
    except:
        return False


def export_cookies(cookie_file, session):
    try:
        with open(cookie_file, "wb") as file:
            pickle.dump(session.cookies, file)
        return True
    except:
        return False

def steam_login():
    # Sign into Steam web

    # Attempt to use saved session
    r = requests.Session()
    if try_recover_cookies(".steamcookies", r) and verify_logins_session(r)[1]:
        return r

    # Saved state doesn't work, prompt user to sign in.
    s_username = input("Steam Username: ")
    user = wa.WebAuth(s_username)
    session = user.cli_login()
    export_cookies(".steamcookies", session)
    return session

def _redeem_steam(session, key, quiet=False):
    # Based on https://gist.github.com/snipplets/2156576c2754f8a4c9b43ccb674d5a5d
    if key == "":
        return 0
    session_id = session.cookies.get_dict()["sessionid"]
    r = session.post("https://store.steampowered.com/account/ajaxregisterkey/", data={"product_key": key, "sessionid": session_id})
    blob = r.json()

    if blob["success"] == 1:
        for item in blob["purchase_receipt_info"]["line_items"]:
            print("Redeemed " + item["line_item_description"])
    
def main():
    session = steam_login()
    with open('keys_generated.txt', 'r') as file:
        for line in file:
            if not valid_steam_key(line):
                print(line + "is not a valid Steam key")
                continue
            else:
                _redeem_steam(session, line)
        

if __name__ == "__main__":
    main()