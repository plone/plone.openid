import random

def GenerateSecret(length=16):
    letters ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letters+="abcdefghijklmnopqrstuvwxyz"
    letters+="01234567890!@#$%^&*()"

    secret=""
    for i in range(length):
        secret+=random.choice(letters)

    return secret

    

