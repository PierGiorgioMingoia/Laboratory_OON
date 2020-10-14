# Lab 1 OON

def es1():
    x = int(input("Enter first value: "))
    y = int(input("Enter second value: "))
    if x * y > 1000:
        return x + y
    else:
        return x * y


def es2(x, y):
    for e in range(x, y + 1):
        print(e + e - 1)


def es3(list):
    n = len(list)
    return list[0] == list[n - 1]


def es4(arr):
    for x in arr:
        if x % 5 == 0:
            print(x)


def es5(string, word):
    return string.count(word)


def es6(arr1, arr2):
    result = []
    for n in arr1:
        if n % 2 != 0:
            result.append(n)
    for n in arr2:
        if n % 2 == 0:
            result.append(n)
    return result


def es7(s1, s2):
    n = int(len(s1) / 2)
    return s1[:n] + s2 + s1[n:]


def es8(s1, s2):
    n1 = len(s1)
    n2 = len(s2)
    return s1[0] + s1[int(n1 / 2)] + s1[n1 - 1] + s2[0] + s1[int(n2 / 2)] + s2[n2 - 1]


def es9():
    string = input("Enter a string with digit, capital, lower: ")
    digits = 0
    low_letters = 0
    upper_letters = 0
    special = 0

    for c in string:
        if c.isdigit():
            digits += 1
        elif c.islower():
            low_letters += 1
        elif c.isupper():
            upper_letters += 1
        elif c.isspace():
            pass
        else:
            special += 1

    return [digits, low_letters, upper_letters, special]


def es10(string, word):
    string = string.lower()
    word = word.lower()
    return string.count(word)


def es11(string):
    count = 0
    sum = 0
    for c in string:
        if c.isdigit():
            count += 1
            sum += int(c)
    return [sum, sum / count]


def es12(string):
    result = {}
    for c in string:
        if c in result:
            result[c] += 1
        else:
            result[c] = 1
    return result


if __name__ == "__main__":
    # print(es1())
    # es2(1, 10)
    # print(es3([1, 2, 4, 5, 6, 1, 2, 0]))
    # es4([1, 2, 3, 5, 10, 120, 500, 5001])
    # print(es5("Emma is a good developer and Emma is also a writer, Emma", "Emma"))
    # print(es6([1, 2, 4, 3], [0, 20, 100, 15]))
    # print(es7("cibaoa", "bomber"))
    # print(es8("ciao", "miao"))
    # print(es9())
    # print(es10("USA sono lo stato più bello del mondo usavano la birra", "USA"))
    # print(es11("1,2,3,5"))
    print(es12("ciaco  asdas adsa asd as 123123"))
