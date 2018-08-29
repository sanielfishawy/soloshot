ars = [1, 2, 3]
def process(a, b):
    return a + b

print ( list(map(lambda a : process(a, 5), ars) ) )