import random
import math
from fractions import gcd

def main():
    p = input("Enter a prime number: ")
<<<<<<< HEAD
    p = int(p)
    q = input("Enter another prime number (Not one you entered above): ")
    q = int(q)
    public_buffer = Find_Public_Key(p,q)
    public_key = public_buffer[0],public_buffer[1]
    private_key = Find_Private_Key_d(public_buffer[0],public_buffer[2],public_buffer[1])
    message = input("Enter a message to encrypt with your public key: ")
    encoded = Encode(message,public_key)
    print ("Public Key: " + str(public_key))
    print ("Private Key: " + str(private_key))
    print ("Encoded Message: " + str(encoded))

    tryit = input("Decode?: [yn]")
    if tryit == 'y' or tryit == 'Y':
        decoded = Decode(encoded,public_key,private_key)
        print ("Decoded Message: " + str(decoded))
=======
    q = input("Enter another prime number (Not one you entered above): ")
    public_buffer = Find_Public_Key(p,q)
    public_key = public_buffer[0],public_buffer[1]
    private_key = Find_Private_Key_d(public_buffer[0],public_buffer[2],public_buffer[1])
    message = raw_input("Enter a message to encrypt with your public key: ")
    encoded = Encode(message,public_key)
    print ("Public Key: " , public_key)
    print ("Private Key: " , private_key)
    print ("Encoded Message: " , encoded)

    tryit = raw_input("Decode?: [yn]")
    if tryit == 'y' or tryit == 'Y':
        decoded = Decode(encoded,public_key,private_key)
        print ("Decoded Message: " , decoded)
>>>>>>> 4f7e1da88d933c7bbc46d62664b163e48b531a9e
    elif tryit == 'n' or tryit == 'N':
        return



def div_alg(a,d):
    quo = 0
    rem = a
    while rem >=d:
        rem = rem - d
        quo = quo + 1
    if a < 0 and r > 0:
        rem = d - rem
        quo = -quo + -1
    return quo,rem

<<<<<<< HEAD
=======
def FME(base,power,mod):
    x = 1
    while 1:
        if power % 2 == 1:
            x = x * base % mod
        power = power/2
        if power == 0:
            break
        base = base * base % mod
    return x

>>>>>>> 4f7e1da88d933c7bbc46d62664b163e48b531a9e
def Euclidean_Alg(m,n):
    while n > 0:
        k = m % n
        m = n
        n = k
    return m

def Convert_Text(s):
    x = []
    for i in s:
        x.append(ord(i))
    return x

def Convert_Num(l):
    new = ""
    for i in range(len(l)):
        new = new + chr(i)
    return new


def Convert_Binary_String(x):
    x = int(bin(x)[2:])
    x = str(x)
    return x

def Find_Public_Key(p,q):
    n = p * q
    m = (p-1) * (q-1)
    e = random.randrange(1,m)
<<<<<<< HEAD
    check = math.gcd(e,m)
    while check!=1 and p == e and q == e:
        e = random.randrange(1,m)
        check = math.gcd(e,m)
=======
    check = gcd(e,m)
    while check!=1 and p == e and q == e:
        e = random.randrange(1,m)
        check = gcd(e,m)
>>>>>>> 4f7e1da88d933c7bbc46d62664b163e48b531a9e
    return (e,n,m)


def Find_Private_Key_d(e,m,n):
    """Uses of extended Euclid algorithm to find multiplicative inverse"""
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_m = m

    while e > 0:
        temp1 = temp_m/e
<<<<<<< HEAD
        temp2 = temp_m - (temp1 * e)
=======
        temp2 = temp_m - temp1 * e
>>>>>>> 4f7e1da88d933c7bbc46d62664b163e48b531a9e
        temp_m = e
        e = temp2
        x = x2 - temp1 * x1
        y = d - temp1 * y1
        x2 = x1
        x1 = x
        d = y1
        y1 = y
    if temp_m == 1:
        d = d + m
    return (d,n)


def Encode(s,public):
    cipher = []
    s = str(s)
    list = Convert_Text(s)

    e = public[0]
    n = public[1]
    bin = Convert_Binary_String(e)
    bin = int(bin,2)
    for i in list:
        cipher.append((i**bin)%n)
    return cipher

def Decode(encoded,public,private):
<<<<<<< HEAD
    decrypted = [chr((i**private[0])%public[1]) for i in encoded]
=======
    decrypted=[]
    for i in encoded:
        #decrypted.append(chr((i**private[0])%public[1]))
        decrypted = [chr((i**private[0])%public[1]) for i in encoded]
>>>>>>> 4f7e1da88d933c7bbc46d62664b163e48b531a9e
    return ''.join(decrypted)

if __name__ == '__main__':
    main()
