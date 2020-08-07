import hashlib

string = "Prejudice"
hashedString = hashlib.sha256(bytes(string, 'utf-8')).hexdigest()

print("String -> ", string)
print("Hashed String -> ", hashedString)