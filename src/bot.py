import requests
from requests.exceptions import HTTPError
import json
import steam.webauth as wa

COOKIES_FILE = "steamcookies.json"

REGISTER_KEY_URL = "https://store.steampowered.com/account/registerkey"
AJAX_REGISTER_KEY_URL = "https://store.steampowered.com/account/ajaxregisterkey/"

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
    for url in REGISTER_KEY_URL:
        r = session.get(url, allow_redirects=False)
        loggedin.append(r.status_code != 301 and r.status_code != 302)
    return loggedin

def try_recover_cookies(cookie_file, session):
    try:
        with open(cookie_file, "r") as file:
            cookies = json.load(file)
            session.cookies.update(cookies)
        return True
    except FileNotFoundError:
        print(f"Cookie file '{cookie_file}' not found.")
        return False
    except PermissionError:
        print(f"Permission denied when accessing cookie file '{cookie_file}'.")
        return False
    except Exception as e:
        print("An error occurred:", str(e))
        return False


def export_cookies(cookie_file, session):
    try:
        with open(cookie_file, "w") as file:
            json.dump(session.cookies.get_dict(), file)
        return True
    except:
        return False

def steam_login():
    # Attempt to use saved session
    r = requests.Session()
    if try_recover_cookies(COOKIES_FILE, r) and verify_logins_session(r)[1]:
        return r

    # Saved state doesn't work, prompt user to sign in.
    s_username = input("Steam Username: ")
    user = wa.WebAuth(s_username)
    session = user.cli_login()
    export_cookies(COOKIES_FILE, session)
    return session

def redeem_steam(session, key):
    if key == "":
        return 0
    session_id = session.cookies.get_dict()["sessionid"]
    try:
        r = session.post(AJAX_REGISTER_KEY_URL, data={"product_key": key, "sessionid": session_id})
        r.raise_for_status()  # Raise an exception for any HTTP errors
        blob = r.json()

        if blob["success"] == 1:
            for item in blob["purchase_receipt_info"]["line_items"]:
                print("Redeemed " + item["line_item_description"] + key)
    except HTTPError as e:
        print("An HTTP error occurred:", str(e))
    except Exception as e:
        print("An error occurred:", str(e))

def main():
    session = steam_login()
    with open('keys_generated.txt', 'r') as file:
        for line in file:
            if not valid_steam_key(line):
                print(line + " is not a valid Steam key")
                continue
            else:
                redeem_steam(session, line)

if __name__ == "__main__":
    main()