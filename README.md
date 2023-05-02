## Example 1: read a file

    d1 = fil.read('file.json')   # Any Json
    d2 = fil.read('file.toml')   # A dict
    d3 = fil.read('file.yaml')   # Any JSON
    d4 = fil.read('file.txt')    # A string

    # Reading a JSON Line file returns an interator:
    for record in fil.read('file.jsonl'):
        print(record)  # A sequence of JSON

## Example 2: write to a file

    fil.write(d1, 'file.json')  # d1 can be any JSON
    fil.write(d2, 'file.toml')  # d2 must be a dict
    fil.write(d3, 'file.yaml')  # d3 can be any JSON
    fil.write(d4, 'file.txt')   # d4 most be a str

    # Write an iterator to a JSON Line file
    dicts = ({'key': i} for i in range(10))
    fil.write(dicts, 'file.jsonl')


### [API Documentation](https://rec.github.io/fil#fil--api-documentation)
