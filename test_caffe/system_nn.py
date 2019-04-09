import numpy as numpy

def main():
    for i in range(0, 4):
        for j in range(0, 4):
            row = list("c({},{}) = ".format(i, j))
            inputs = ["a", "b"]
            weights = ["α", "β"]
            for k in range(len(inputs)):
                for p in range(-1, 2):
                    for s in range(-1, 2):
                        if i + p >= 0 and j + s >= 0:
                            row += list("{}({},{}){}({},{}) + ".format(weights[k], p, s, inputs[k], i + p, j + s))
                        else:
                            row += list("{}({},{})0 + ".format(weights[k], p, s))
            print("".join(row))
            

if __name__ == "__main__":
    main()