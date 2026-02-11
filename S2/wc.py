import sys

# número de linhas
def count_lines(file):
    with open(file) as f:
        return len(f.readlines())

# número de palavras

def count_words(file):
    with open(file) as f:
        return len(f.read().split())
    
# número de caracteres

def count_characters(file):
    with open(file) as f:
        return len(f.read())

def main(inp):

    if len(inp) != 2:
        print("Usage: wc.py <file>")
        return
    
    file = inp[1]
    print(f"Lines: {count_lines(file)}")
    print(f"Words: {count_words(file)}")
    print(f"Characters: {count_characters(file)}")

if __name__ == "__main__":
    main(sys.argv)