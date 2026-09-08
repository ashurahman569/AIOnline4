import math
import random
import time

class TSP:
    def __init__(self):
        self.graph = []
        self.min_cost = math.inf
        self.best_path = []

    def readInput(self, filename):
        with open(filename, 'r') as f:
            self.N = int(f.readline())
            self.visited = [False] * self.N
            self.graph = []
            for i in range(self.N):
                row = list(map(int, f.readline().split()))
                self.graph.append(row)
            
    def addrow (self, row):
        self.graph.append(row)

    def copy(self, other):
        self.N = other.N
        self.graph = [row[:] for row in other.graph]
        self.visited = other.visited[:]
        self.min_cost = other.min_cost
        self.best_path = other.best_path[:]

    def greedyTSP(self):
        self.visited[0] = True
        start_time = time.time()
        current = 0
        path = [0]
        for i in range(1, self.N):
            next_city = -1
            min_cost = math.inf
            for j in range(self.N):
                if not self.visited[j] and self.graph[current][j] < min_cost:
                    min_cost = self.graph[current][j]
                    next_city = j
            path.append(next_city)
            self.visited[next_city] = True
            current = next_city
        self.greedyTSP_time = time.time() - start_time
        path.append(0)  # Return
        return path

    def calculateTourCost(self, path): #takes path array as input, returns string 
        cost = 0
        prev = -1
        printstring = ""
        for i in path:
            if prev != -1:
                printstring += f"-> {i} "
                cost += self.graph[prev][i]
            else:
                printstring += str(i) + " "
            prev = i
        #print(printstring)
        return cost, printstring

    def isSymmetric(self):
        for i in range(self.N):
            for j in range(i + 1, self.N):
                if self.graph[i][j] != self.graph[j][i]:
                    return False
        return True

    def pickReversalIndices(self):
        index1 = random.randint(1, self.N - 2)
        index2 = random.randint(index1 + 1, self.N - 1)
        return index1, index2

    def generateNeighbor(self, path):
        if self.N < 3:
            return path
        index1, index2 = self.pickReversalIndices()
        for i in range((index2 - index1 + 1) // 2):
            path[index1 + i], path[index2 - i] = path[index2 - i], path[index1 + i]
        return path

    def reversalDelta(self, path, index1, index2, symmetric):
        prevCity = path[index1 - 1]
        afterCity = path[index2 + 1]
        a = path[index1]
        b = path[index2]

        oldBoundary = self.graph[prevCity][a] + self.graph[b][afterCity]
        newBoundary = self.graph[prevCity][b] + self.graph[a][afterCity]
        delta = newBoundary - oldBoundary

        if not symmetric:
            oldInternal = 0
            newInternal = 0
            for t in range(index1, index2):
                oldInternal += self.graph[path[t]][path[t + 1]]
                newInternal += self.graph[path[t + 1]][path[t]]
            delta += newInternal - oldInternal

        return delta

    def reverseSegment(self, path, index1, index2):
        lo, hi = index1, index2
        while lo < hi:
            path[lo], path[hi] = path[hi], path[lo]
            lo += 1
            hi -= 1

    def simulatedAnnealing(self, T0, alpha, Tmin, MaxIter, iterPerTemp=100, useGreedy=False, seed=None):
        if seed is not None:
            random.seed(seed)

        start_time = time.time()

        if useGreedy:
            path = self.greedyTSP()
        else:
            path = self.generateRandomTour()

        C_current, initial = self.calculateTourCost(path)
        print("Initial Solution:")
        print(initial)
        print(f"Initial Cost: {C_current}")
        initial_cost = C_current

        best_path = path[:]
        best_cost = C_current

        symmetric = self.isSymmetric()

        T = T0
        totalIter = 0
        acceptedMoves = 0
        worseAccepted = 0

        while T > Tmin and totalIter < MaxIter:
            for i in range(iterPerTemp):
                if totalIter >= MaxIter:
                    break

                if self.N < 3:
                    totalIter += 1
                    continue

                index1, index2 = self.pickReversalIndices()
                Delta = self.reversalDelta(path, index1, index2, symmetric)

                if Delta <= 0:
                    self.reverseSegment(path, index1, index2)
                    C_current += Delta
                    acceptedMoves += 1
                    if C_current < best_cost:
                        best_cost = C_current
                        best_path = path[:]
                else:
                    p = math.exp(-Delta / T)
                    if random.random() < p:
                        self.reverseSegment(path, index1, index2)
                        C_current += Delta
                        acceptedMoves += 1
                        worseAccepted += 1

                totalIter += 1

            T *= alpha

        end_time = time.time()

        self.sa_iterations = totalIter
        #self.sa_initial_cost = initial_cost
        self.sa_best_cost = best_cost
        self.sa_accepted_moves = acceptedMoves
        self.sa_worse_accepted = worseAccepted
        self.sa_execution_time = end_time - start_time

        return best_path

    def printResults(self, path):
        cost, pathstring = self.calculateTourCost(path)
        print(f"Path: {pathstring}")
        print(f"Cost: {cost}")
    
    def generateRandomTour(self):
        path = list(range(1,self.N))
        random.shuffle(path)
        path = [0] + path + [0]
        return path
        
        
def main():
    Temps = [100,1000,5000]
    Alphas = [0.9,0.95,0.995]
    TempAlphaPairs = [(T, A) for T in Temps for A in Alphas]
    tsp = TSP()
    tsp.readInput('input1.txt') 

    tsp1 = TSP()
    tsp1.copy(tsp)
    print("Greedy TSP:")
    path1 = tsp1.greedyTSP()
    greedycost, greedytour = tsp1.calculateTourCost(path1)
    print("Tour:")
    print(greedytour)
    print(f"Total Cost: {greedycost}")
    print(f"Execution Time: {tsp1.greedyTSP_time:.4f} seconds")

    for T0, alpha in TempAlphaPairs: 
        print(f"\nRunning Simulated Annealing with T0={T0} and alpha={alpha}\n")   
        # tsp2 = TSP()
        # tsp2.copy(tsp)
        # print("\nRandom TSP:")
        # path2 = tsp2.generateRandomTour()
        # tsp2.printResults(path2)
        tsp3 = TSP()
        tsp3.copy(tsp)
        print("\nSimulated Annealing:")
        path3 = tsp3.simulatedAnnealing(T0, alpha, Tmin=0.001, MaxIter=100000, iterPerTemp=100, useGreedy=True, seed = 42)
        sacost, satour = tsp3.calculateTourCost(path3)
        print("Best Tour Found:")
        print(satour)
        print(f"Best Cost: {sacost}")
        print(f"Initial Temperature: {T0}")
        print(f"Cooling Rate: {alpha}")
        print(f"Total Iterations: {tsp3.sa_iterations}")
        #print(f"Initial Cost: {tsp3.sa_initial_cost}")
        # print(f"Best Cost: {tsp3.sa_best_cost}")
        print(f"Accepted Moves: {tsp3.sa_accepted_moves}")
        print(f"Worse Moves Accepted: {tsp3.sa_worse_accepted}")
        print(f"Execution Time: {tsp3.sa_execution_time:.4f} seconds")

        print("\nComparison:")
        print(f"Greedy Cost: {greedycost}")
        print(f"Simulated Annealing Cost: {sacost}")
        improv = ((greedycost - sacost) / greedycost) * 100
        print(f"Improvement Percentage: {improv:.2f}%")
        print("Best Method for this run: ")
        print("Simulated Annealing" if sacost < greedycost else "Greedy TSP" if sacost > greedycost else "Both methods produced the same cost.")

if __name__ == '__main__':
    main()
