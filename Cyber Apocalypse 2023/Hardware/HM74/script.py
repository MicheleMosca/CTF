#!/bin/python3

def check(sequence):
    p0 = int(sequence[0])
    p1 = int(sequence[1])
    p2 = int(sequence[3])

    data0 = int(sequence[6])
    data1 = int(sequence[5])
    data2 = int(sequence[4])
    data3 = int(sequence[2])

    wrong = [0, 0, 0]

    #print(sequence)

    if p0 != (data3 ^ data2 ^ data0):
        wrong[0] = 1
        #print("p0 wrong!")

    if p1 != (data3 ^ data1 ^ data0):
        wrong[1] = 1
        #print("p1 wrong!")

    if p2 != (data2 ^ data1 ^ data0):
        wrong[2] = 1
        #print("p2 wrong!")



    if wrong[1] == 1 and wrong[2] == 1 and wrong[0] == 0:
        #print("Data1 is wrong!")
        data1 = int(not data1)

    elif wrong[0] == 1 and wrong[2] == 1 and wrong[1] == 0:
        #print("Data2 is wrong!")
        data2 = int(not data2)

    elif wrong[0] == 1 and wrong[1] == 1 and wrong[2] == 0:
        #print("Data3 is wrong!")
        data3 = int(not data3)

    elif wrong[0] == wrong[1] == wrong[2] == 1:
        #print("Data0 is wrong!")
        data0 = int(not data0)

    #print("Correct Data:")

    data = str(data3) + str(data2) + str(data1) + str(data0)

    return hex(int(data, 2))[2]

    #print("-----------------------")


code = "1101000111000001001011001100101010101010100001011010001101001101110000010011010101010100100101000101001011101111100101100011110000011010100000010111000100110011011000100100101111111000010111000111100000100011010100010101010110100000000011010110011111111100110110100010101101000110010010010010111001001110110100010011011001100101110100111000001110100110000110101101010010111111110001101000100110000010000000000001001001010110101111111111001101000010111001010011001100010101011001001001111111110011010010010101111011001010000110101111000011100110111100100010100111011101000011000111101011000110101111111110010111001101100011010100000000001110001111011011111110101010001100001100111000110011001001000111010011110101101100110001010011001100110100101001101111110100101111011110000110001111010100111111110001011100111001001011111111100001111000101100111000011011001100000011010000110010111100110110010011001101111100100001100110001010000001100100011111010000"

d = {}
for i in range(0, len(code), 7):
    d[i] = ''

with open("signals.txt") as f:
    for line in f:
        code = line[10:].strip()
        s = ''
        for i in range(0, len(code), 7):
            s += check(code[i:i+7])
            d[i] += check(code[i:i+7])
        try:
            print(bytes.fromhex(s).decode())
        except:
            pass

s = ''
for v in d.values():
    s += max(set(v), key=v.count)

print(bytes.fromhex(s).decode())