#!/usr/bin/python
# vim: sw=4 ts=4 softtabstop=4 expandtab
"""
    Compute the minimum edit distance
    between two strings using the
    Wagner-Fischer algorithm. Then compute
    all possible sequences of operations that
    give the minimum edit distance
"""
import argparse
import logging
import sys

skipNoOps = False

class Insertion:
    cost = 1
    @staticmethod
    def getDependentCellIndices(i,j):
        if i==0 and j==0:
            raise ArithmeticError()
        else:
            return (i,j-1)
    @staticmethod
    def getVerb():
        return 'Insert'

class Deletion:
    cost = 1
    @staticmethod
    def getDependentCellIndices(i,j):
        if i==0 and j==0:
            raise ArithmeticError()
        else:
            return (i-1,j)
    @staticmethod
    def getVerb():
        return 'Delete'

class Substitution:
    cost = 1
    def getDependentCellIndices(i,j):
        if i==0 and j==0:
            raise ArithmeticError()
        else:
            return (i-1,j-1)
    @staticmethod
    def getVerb():
        return 'Substitute'

class NoOp:
    cost = 0
    def getDependentCellIndices(i,j):
        if i==0 and j==0:
            raise ArithmeticError()
        else:
            return (i-1,j-1)

    @staticmethod
    def getVerb():
        return 'NoOp'


class Distance:
    def __init__(self, value=0):
        self.value = value
        self.operations = [ ] # used for backtracing the table

def computeEditDistance(initialString, finalString):
    logging.info("Calculating edit distance '{}' => '{}'".format(initialString, finalString))

    # Create (m+1)x(n+1) table
    table = [ [ Distance(0) for j in range(0, len(finalString) +1)] 
              for i in range(0, len(initialString) +1) 
            ]

    # Initialisation
    for i in range(0, len(initialString) +1):
        table[i][0].value = Deletion.cost * i
        if i != 0:
            table[i][0].operations.append( Deletion )

    # Initialisation
    for j in range(0, len(finalString) +1):
        table[0][j].value = Insertion.cost * j
        if j != 0:
            table[0][j].operations.append( Insertion )

    logging.info('Finished initialising')
    printTable(table, initialString, finalString)

    for i in range(1, len(initialString) +1):
        for j in range(1, len(finalString) +1):
            initalStringIndex = i - 1
            finalStringIndex = j - 1

            # Calculate the cost of each type of operation and pair with the type
            # of operation which will be stored for backtracing later
            costs= [ (table[i][j-1].value + Insertion.cost, Insertion ),
                     (table[i-1][j].value + Deletion.cost, Deletion ),
                     (table[i-1][j-1].value + Substitution.cost, Substitution)
                   ]

            if initialString[initalStringIndex] == finalString[finalStringIndex]:
                costs.append( (table[i-1][j-1].value, NoOp) )

            # Do in-place sort, sorting by the cost of the operation
            costs.sort(key= lambda pair: pair[0])

            # Record the minimum cost
            table[i][j].value = costs[0][0]

            # Record the operation(s) that give the minimum cost for
            # backtracing purposes
            previousCost = costs[0][0]
            for (costValue, costType) in costs:
                if costValue > previousCost:
                    break

                table[i][j].operations.append( costType )

    logging.info('Calculation complete')
    printTable(table, initialString, finalString)
    return table

def printTable(table, initialString, finalString):
    m = len(table)
    n = len(table[0])

    row_format = "{:^5}" * ( len(finalString) +2 )
    header = list("  ")
    header.extend(finalString)
    print(row_format.format(*header))

    for rowNum in range(0, len(initialString) + 1 ):
        row = [ ]
        if rowNum == 0:
            row.append(' ')
        else:
            row.append( initialString[ rowNum -1 ])

        row += [ ed.value for ed in table[rowNum] ]
        print(row_format.format(*row))

def computeOperations(table, initialString, finalString, recordNoOps):
    from collections import namedtuple
    import copy
    Operation = namedtuple('Operation', ['point','op'])
    # list of list of Operation tuples
    incomplete_solutions = [ ]
    complete_solutions = [ ]

    i = len(initialString)
    j = len(finalString)
    d = table[i][j]


    # Push on the initial solutions
    for op in d.operations:
        incomplete_solutions.append( [ Operation(point=(i,j), op=op) ] )
        logging.info('Added initial solution')

    while len(incomplete_solutions) > 0:
        solution = incomplete_solutions.pop()
        current = solution[-1]
        i = current.point[0]
        j = current.point[1]

        logging.info('Staring solution at {},{}'.format(i,j))


        # Compute remainder of solution
        while not (i == 0 and j == 0):
            new_location = current.op.getDependentCellIndices(i,j)
            i = new_location[0]
            j = new_location[1]
            
            nextCell = table[i][j]

            # Loop over operations, if there is more than one operation
            # we need to generate a new solution starting from this point
            numberOfOperationsAdded=0
            for op in nextCell.operations:
                newOperation = Operation(point=(i,j), op=op)

                if op == NoOp and not recordNoOps:
                    logging.info('Skipping NoOp at ({},{})'.format(i,j))
                    current = newOperation
                    continue

                if numberOfOperationsAdded == 0:
                    logging.info('Adding new operation at ({i},{j})'.format(i=i,j=j))
                    current = newOperation
                    solution.append(newOperation)
                else:
                    # There is more than one path we can take so we need
                    # to make more solutions and follow them later
                    logging.info('Forking new operation at ({i},{j})'.format(i=i,j=j))
                    newSolution = copy.deepcopy( solution )
                    newSolution.append(newOperation)
                    incomplete_solutions.append( newSolution )

                numberOfOperationsAdded += 1



        # The current solution is now complete

        # Reverse the order of operations so we present in correct order
        solution.reverse()
        complete_solutions.append(solution)
    
    logging.info('Computed {} solution(s)'.format(len(complete_solutions)))
    return complete_solutions

def printSolution(solution, initialString, finalString):
    for op in solution:
        msg = op.op.getVerb() + " "
        if op.op == Insertion:
            msg += "'{}'".format(finalString[ op.point[1] -1])
        elif op.op == Deletion:
            msg += "'{}'".format(initialString[ op.point[0] -1])
        elif op.op == Substitution:
            msg += "'{}' for '{}'".format(initialString[ op.point[0] -1],
                                          finalString[ op.point[1] -1])
        elif op.op == NoOp:
            msg += "'{}' = '{}'".format(initialString[ op.point[0] -1],
                                          finalString[ op.point[1] -1])

        else:
            raise Exception('Unsupported op')

        print(msg)

    print("")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('initial_string')
    parser.add_argument('final_string')
    parser.add_argument('--record_noops', help='Record noops in solutions',action='store_true')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    initialString = args.initial_string
    finalString = args.final_string
    ed = computeEditDistance(initialString, finalString)
    minimumEditDistance = ed[len(initialString)][len(finalString)].value
    logging.info("Minimum edit distance is {}".format(minimumEditDistance))
    solutions = computeOperations(ed, initialString, finalString, args.record_noops)

    for (index,s) in enumerate(solutions):
        logging.info("Solution: {}".format(index))
        printSolution(s, initialString, finalString)
