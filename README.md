## Example 1: read a file

    # Reading a JSON Line file returns an interator:
    for record in fil.read('file.jsonl'):
        ...

## Example 2: write a file

    fil.write(d3, 'file.json')
    fil.write(d2, 'file.toml')
    fil.write(d1, 'file.yaml')

    # Write an iterator to a JSON Line file
    dicts = ({'key': i} for i in range(10))
    fil.write(dicts, 'file.jsonl')


### [API Documentation](https://rec.github.io/fil#fil--api-documentation)
