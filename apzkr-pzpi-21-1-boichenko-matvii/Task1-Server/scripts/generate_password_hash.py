import sys

from fastapi_users.password import PasswordHelper

password = "" if len(sys.argv) != 2 else sys.argv[1]
if not password:
    password = input("Enter password: ")
    if not password:
        raise ValueError("Pass a password value to the script")

helper = PasswordHelper()
hash = helper.hash(password)
print("Hash:", hash)

inpt = input("Re-enter pwd to check:")
print("Res:", helper.verify_and_update(inpt, hash))
