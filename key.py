from cryptography.fernet import Fernet

def generate_key():
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
                key_file.write(key)

def load_key():
    return open("key.key", "rb").read()

def encrypt_message(mess):
        key = load_key()
        encoded_mess = mess.encode()
        crypter = Fernet(key)
        encrypted_message = crypter.encrypt(encoded_mess)

        return encrypted_message

def decrypt_message(decrypt_mess):
        key = load_key()
        crypter = Fernet(key)
        decrypted_message = crypter.decrypt(decrypt_mess)

        return decrypted_message.decode()

if __name__ == "__main__":
        text = encrypt_message("oh shiet")
        print(text)
        detext = decrypt_message(text)
        print(detext)
        
        check = str(text[:2])
        if check == "b'gA'":
                print("ok ok ok")

        text = str(text)
        length = len(text)
        print(length)
        if length > 30:
                print(">30 right")
        text = bytes(text[2:length - 1], "utf8")
        print(text)
        print(decrypt_message(text))

        if decrypt_message(text) == "oh shiet":
                print("true") 


        
        

      

