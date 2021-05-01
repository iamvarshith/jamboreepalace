def findSum(numbers, queries):
    k = []
    sum = 0
    for i in range(len(queries)):
        for j in range(len(queries[i])):
            k.append(queries[i][j])

    for l in range(k[0] + 1, k[1]):
        if numbers[l] != 0:
            sum = sum + numbers[l]
        else:
            sum += k[2]
    print(numbers)
    print(sum)

    if __name__ == '__main__':
        fptr = open(os.environ['OUTPUT_PATH'], 'w')
        numbers_count = int(input().strip())

        numbers = []

        for _ in range(numbers_count):
            numbers_item = int(input().strip())
            numbers.append(numbers_item)

        queries_rows = int(input().strip())
        queries_columns = int(input().strip())

    queries = []

    for _ in range(queries_rows):
        queries.append(list(map(int, input().rstrip().split())))

    result = findSum(numbers, queries)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
