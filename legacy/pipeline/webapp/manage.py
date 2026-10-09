"""
manage.py
---------
CLI-only account management. Creating the first admin account must not be
a web route -- an unauthenticated "create admin" form would be a
privilege-escalation hole on a tool that might still be network-reachable.

Usage:
    python3 webapp/manage.py create-admin --username admin --password ...
    python3 webapp/manage.py create-intern --username jane --password ...
    python3 webapp/manage.py list-users
"""
import argparse
import getpass
import sys

import db
from auth import hash_password


def create_user(username, password, role):
    db.init_db()
    if db.users_get_by_username(username):
        print(f"User '{username}' already exists.", file=sys.stderr)
        sys.exit(1)
    db.users_create(username, hash_password(password), role)
    print(f"Created {role} account '{username}'.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    for cmd, role in (("create-admin", "admin"), ("create-intern", "intern")):
        p = sub.add_parser(cmd)
        p.add_argument("--username", required=True)
        p.add_argument("--password", help="Prompted securely if omitted")

    sub.add_parser("list-users")

    args = ap.parse_args()
    db.init_db()

    if args.cmd == "list-users":
        for u in db.users_list():
            status = "active" if u["active"] else "disabled"
            print(f"  {u['username']:<20} {u['role']:<10} {status}")
        return

    role = "admin" if args.cmd == "create-admin" else "intern"
    password = args.password or getpass.getpass(f"Password for '{args.username}': ")
    create_user(args.username, password, role)


if __name__ == "__main__":
    main()
