import numpy as np


def es1():
    x = np.random.rand(4, 2)
    return x


def es2():
    x = np.arange(100, 200, 10)
    x = x.reshape(5, 2)
    return x


def es3():
    arr = np.array([[11, 22, 33], [44, 55, 66], [77, 88, 99]])
    result = []
    # can be done with [...] result = arr[...,2]
    for x in arr:
        result.append(x[2])

    return result


def es4():
    arr = np.array([[3, 6, 9, 12], [15, 18, 21, 24], [27, 30, 33, 36], [39, 42, 45, 48], [51, 54, 57, 60]])
    result = arr[1::2, ::2]
    return result


def es5():
    arr1 = np.array([[5, 6, 9], [21, 18, 27]])
    arr2 = np.array([[15, 33, 24], [4, 7, 1]])
    arr3 = arr1 + arr2

    for num in np.nditer(arr3, op_flags=['readwrite']):
        num[...] = np.sqrt(num)
    return arr3


def es6(np_array):
    return np.sort(np_array)


def es7(np_array):
    result = np.delete(np_array, 1, axis=1)
    arr = np.array([10, 10, 10])
    result = np.insert(result, 1, arr, axis=1)

    return result


if __name__ == "__main__":
    # print(es1())
    # print(es2())
    # print(es3())
    # print(es4())
    # print(es5())
    # print(es6(np.array([[5, 6, 9], [21, 18, 27]])))
    print(es7(np.array([[5, 6, 9], [21, 18, 27], [21, 18, 27]])))
