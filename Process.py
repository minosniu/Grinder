__author__ = 'minosniu'

### Console application to align, reshape, filter, average (maybe) data


if __name__ == '__main__':
    """
    Provide the following arguments when running from console:
        - name of the source file
        - address of the Freezer database
        - name of the analyst
    Example:
        $python Grinder.py 100 200 "./fpga" "localhost:27017" "Minos Niu"
    """
    import sys

    # query = sys.argv[1]
    # addr = sys.argv[7]
    addr = 'mongodb://localhost:27017/'
    query = """{"analystName": "Minos Niu",
    "gammaDyn": 100,
    "gammaSta": 100}
     """

