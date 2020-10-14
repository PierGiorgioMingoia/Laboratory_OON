def es1(l1, l2):
    result = []
    for i, value in enumerate(l1):
        if i % 2 != 0:
            result.append(value)
    for i, value in enumerate(l2):
        if i % 2 == 0:
            result.append(value)
    return result


def es2(l):
    if len(l) < 5:
        return "Errore"
    n = l[4]
    l.pop(4)
    l.append(n)
    l.insert(0, n)
    return l


import pprint


def es3(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def es4(lst):
    result = {}
    for c in lst:
        if c in result:
            result[c] += 1
        else:
            result[c] = 1
    return result


def es5(l1, l2):
    result = set()
    for x in l1:
        if x in l2:
            result.add(x)
    return result


def es6(s1, s2):
    intersection = s1.intersection(s2)
    for x in intersection:
        s1.remove(x)
    return s1


def es7(s1, s2):
    sub = True
    for x in s1:
        if x not in s2:
            sub = False
            return "No sub set"
    return s2 - s1


def es8(lst, dict):
    for i, x in enumerate(lst):
        found = False
        for key, value in dict.items():
            if x == value:
                found = True
        if not found:
            lst.pop(i)
    return lst


def es9(d):
    results = set()
    for key, value in d.items():
        results.add(value)
    return results


def es10(lst):
    lst = list(dict.fromkeys(lst))
    max = lst[0]
    min = lst[0]
    for e in lst:
        if e > max:
            max = e
        if e < min:
            min = e
    return (max, min)


if __name__ == "__main__":
    print(es1([3, 412, 4, 36, 643, 12], [123, 2, 865, 0]))
    print(es2([123, 213, 1, 132, 0, 213, 235, 34543]))
    pprint.pprint((list(es3([1, 2, 3, 4, 5, 6, 7, 8, 9], 3))))
    print(es4([11, 45, 8, 11, 23, 45, 23, 45, 89]))
    print(es5([2, 3, 4, 5, 6, 7, 8], [4, 9, 16, 25, 36, 49, 64]))
    print(es6({1, 2, 3, 4}, {1, 432, 36, 342, 213, 4}))
    print(es7({1, 2, 3}, {1, 2, 3, 4, 5}))
    print(es8([10, 8, 21, 54, 33], {'A': 10, 'B': 21, 'C': 33}))
    print(es9({'Jan': 10, 'June': 10, 'March': 123}))
    print(es10([10, 12, 321, 4, -12, 23, 50]))
