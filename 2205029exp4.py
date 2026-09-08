
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

    def generateNeighbor(self, path):
        if self.N < 3:
            return path
        index1 = random.randint(1, self.N - 2)
        index2 = random.randint(index1 + 1, self.N - 1)
        for i in range((index2 - index1 + 1) // 2):
            path[index1 + i], path[index2 - i] = path[index2 - i], path[index1 + i]
        return path

    def simulatedAnnealing(self, T0, alpha, Tmin, MaxIter, iterPerTemp=100, useGreedy=False, seed=None):
        if seed is not None:
            random.seed(seed)

        start_time = time.time()

        if useGreedy:
            path = self.greedyTSP()
        else:
            path = self.generateRandomTour()

        C_current, initial = self.calculateTourCost(path)
        initial_cost = C_current

        best_path = path[:]
        best_cost = C_current

        T = T0
        totalIter = 0
        acceptedMoves = 0
        worseAccepted = 0

        while T > Tmin and totalIter < MaxIter:
            for i in range(iterPerTemp):
                if totalIter >= MaxIter:
                    break

                candidate = self.generateNeighbor(path[:])
                C_new, _ = self.calculateTourCost(candidate)
                Delta = C_new - C_current

                if Delta <= 0:
                    path = candidate
                    C_current = C_new
                    acceptedMoves += 1
                    if C_current < best_cost:
                        best_cost = C_current
                        best_path = path[:]
                else:
                    p = math.exp(-Delta / T)
                    if random.random() < p:
                        path = candidate
                        C_current = C_new
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
    tsp = TSP()
    tsp.readInput('input4.txt') 
    T0 = 100
    alpha = 0.995

    print(f"\nRunning Simulated Annealing with T0={T0} and alpha={alpha}")   
    bestrandcost = math.inf
    worstrandcost = -math.inf
    totalrandcost = 0
    totalexecutiontime = 0
    print("\nSimulated Annealing with random initial tour:")
    for i in range(5):
        tsp1 = TSP()
        tsp1.copy(tsp)
        
        path1 = tsp1.simulatedAnnealing(T0, alpha, Tmin=0.001, MaxIter=100000, iterPerTemp=100, useGreedy=False, seed=None)
        sacost, satour = tsp1.calculateTourCost(path1)
        totalrandcost += sacost
        totalexecutiontime += tsp1.sa_execution_time
        if sacost < bestrandcost:
            bestrandcost = sacost
        if sacost > worstrandcost:
            worstrandcost = sacost

    avgrandcost = totalrandcost / 5
    avgexecutiontime = totalexecutiontime / 5
    print(f"Best Cost: {bestrandcost}")
    print(f"Average Cost: {avgrandcost}")    
    print(f"Worst Cost: {worstrandcost}")
    print(f"Average Execution Time: {avgexecutiontime:.4f} seconds")

    bestgreedycost = math.inf
    worstgreedycost = -math.inf
    totalgreedycost = 0
    totalgreedyexecutiontime = 0
    print("\nSimulated Annealing with Greedy TSP:")
    for j in range(5):
        tsp2 = TSP()
        tsp2.copy(tsp)
        
        path2 = tsp2.simulatedAnnealing(T0, alpha, Tmin=0.001, MaxIter=100000, iterPerTemp=100, useGreedy=True, seed=None)
        greedycost, greedytour = tsp2.calculateTourCost(path2)
        totalgreedycost += greedycost
        totalgreedyexecutiontime += tsp2.sa_execution_time
        if greedycost < bestgreedycost:
            bestgreedycost = greedycost
        if greedycost > worstgreedycost:
            worstgreedycost = greedycost

    avggreedycost = totalgreedycost / 5
    avggreedyexecutiontime = totalgreedyexecutiontime / 5
    print(f"Best Cost: {bestgreedycost}")
    print(f"Average Cost: {avggreedycost}")    
    print(f"Worst Cost: {worstgreedycost}")
    print(f"Average Execution Time: {avggreedyexecutiontime:.4f} seconds")
if __name__ == '__main__':
    main()
    
    