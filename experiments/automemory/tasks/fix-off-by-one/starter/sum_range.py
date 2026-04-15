def sum_range(a, b):
    total = 0
    for i in range(a, b):
        total += i
    return total


if __name__ == "__main__":
    print(sum_range(1, 10))
