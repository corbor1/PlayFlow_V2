import bcrypt


salt = bcrypt.gensalt()
print (salt)
password_bytes = "test".encode("utf-8")   # plain-text пароль
print (f"Переменная password_bytes = {password_bytes}")
hashed = bcrypt.hashpw(password_bytes, salt)
print (f"Переменная hashed = {hashed}")

password_hash_str = hashed.decode("utf-8")
print (f"Переменная password_hash_str = {password_hash_str}")

