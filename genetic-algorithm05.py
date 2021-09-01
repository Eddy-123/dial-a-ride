import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt, collections
from datetime import datetime

class Instance:
    number_of_vehicles = None
    number_of_services = None
    vehicle_capacity = None
    maximum_ride_time = None
    depot = None
    vertices = []
    starting_time = {
        'pr01': [188.54, 148.08, 83.13],
        'pr02': [98.25, 85.24, 130.29, 54.96, 79.93],
        'pr03': [43.59, 125.08, 99.04, 125.01, 70.93, 80.93, 137.01],
        'pr05': [136.50, 90.32, 97.37, 112.42, 88.77, 69.00, 161.34, 301.39, 33.37, 143.39, 104.44]
        }
    name = 'pr05'
    
    @classmethod
    def read(cls, instance_path = 'instances/pr05.txt'):
        cls.vertices = []
        with open(instance_path, 'r') as f:
            file_content = f.readlines()[:]
            
            datas = file_content[2:]
            
            #general information
            instance_description = file_content[0]
            instance_description = instance_description.split()
            cls.number_of_vehicles = int(instance_description[0])
            cls.number_of_services = int(instance_description[1])
            cls.maximum_route_duration = float(instance_description[2])
            cls.vehicle_capacity = int(instance_description[3])
            cls.maximum_ride_time = float(instance_description[4])
            
            
            #depot
            depot = file_content[1]
            depot = depot.split()
            cls.depot = Vertice(number = depot[0], x_coordinate = depot[1], y_coordinate = depot[2], service_time_duration = depot[3], service_nature = depot[4], service_early_time = depot[5], service_later_time = depot[6])
            
        for data in datas:
            data = data.split()
            vertice = Vertice(number = data[0], x_coordinate = data[1], y_coordinate = data[2], service_time_duration = data[3], service_nature = data[4], service_early_time = data[5], service_later_time = data[6])
            cls.vertices.append(vertice)
    
    @classmethod
    def get_vertice(cls, vertice_number):
        if vertice_number == 0:
            return Instance.depot
        for vertice in Instance.vertices:
            if vertice.number == vertice_number:
                return vertice
        

class Vertice:
    def __init__(self, number, x_coordinate, y_coordinate, service_time_duration, service_nature, service_early_time, service_later_time):
        self.number = int(number)
        self.x_coordinate = float(x_coordinate)
        self.y_coordinate = float(y_coordinate)
        self.service_time_duration = float(service_time_duration)
        self.service_nature = int(service_nature)
        self.service_early_time = float(service_early_time)
        self.service_later_time = float(service_later_time)
        #to do : values set to -1 must be reset
        self.vehicle_arrival_time = -1
        self.departure_time = -1
        self.begin_service_time = -1
        
        self.violation_load = -1
    
    def distance(self, vertice):
        x_distance = abs(self.x_coordinate - vertice.x_coordinate)
        y_distance = abs(self.y_coordinate - vertice.y_coordinate)
        distance = np.sqrt((x_distance**2) + (y_distance**2))
        return distance
    
    def __repr__(self):
        return "(" + str(self.x_coordinate) + ", " + str(self.y_coordinate) + ")"

#Global call
Instance.read()

class Fitness:
    def __init__(self, route):
        self.route = route                
        self.distance = 0 #self.route_distance()
        self.fitness = 0 #self.route_fitness()
        violation_load = 0
    
    def route_distance(self):
        path_distance = 0
        for i in range(0, (len(self.route) - 1)):#complete route
            from_vertice = self.route[i]
            to_vertice = self.route[i+1]
            path_distance += from_vertice.distance(to_vertice)
        self.distance = path_distance
        return self.distance
    
    def route_cost(self): #routing cost = sum(c_i_j)
        return self.route_distance()
    
    def route_travel_time(self):
        return self.route_distance()
    
    def route_ride_time(self):
        return self.route_distance()
    
    def route_duration(self, starting_time = 0):
        services_time_duration = 0
        path_distance = 0
        ending_time = starting_time
        for i in range(len(self.route) - 1):
            services_time_duration = self.route[i].service_time_duration
            from_vertice = self.route[i]
            to_vertice = self.route[i+1]
            
            path_distance = from_vertice.distance(to_vertice)
            waiting_time = to_vertice.service_early_time - (ending_time + services_time_duration + path_distance)
            transit_time = (ending_time + services_time_duration + path_distance) - to_vertice.service_later_time
            if waiting_time < 0:
                waiting_time = 0
            ending_time += services_time_duration + path_distance + waiting_time
        route_duration = ending_time - starting_time
        return route_duration
    
    def route_fitness(self):
        c_routing_cost = self.route_cost()
        q_violation_load = self.violation_load
        d_violation_duration = max(0, Instance.maximum_route_duration - self.route_duration())
        w_violation_time_window = self.route_violation_time_window()
        t_violation_ride_time = max(0, Instance.maximum_ride_time - self.route_ride_time())
        fitness = self.route_distance()
        return fitness
    
    def route_violation_time_window(self): #one route
        for i in range(len(self.route)):
            vertice = self.route[i]
            service_begin_time = max(vertice.service_early_time, vertice.vehicle_arrival_time)
            x = service_begin_time - vertice.service_later_time
            x = max(0, x)
            route_violation_time_window += x
        return route_violation_time_window
    
    def request_violation_ride_time(self, request_origin_vertice, request_destination_vertice): #one request
        request_ride_time = request_destination_vertice.begin_service_time - request_origin_vertice.departure_time
        x = request_ride_time - Instance.maximum_ride_time
        request_violation_ride_time = max(0, x)
        return request_violation_ride_time
    
    @classmethod
    def individual_evaluation(cls, individual, instance_name = Instance.name):
        starting_time = Instance.starting_time[instance_name] # [188.54, 148.08, 83.13]
        total_duration = 0
        total_route_cost = 0


        for i in range(len(individual.sequences)):
            fitness = Fitness(individual.sequences[i+1])
            route_duration  = fitness.route_duration(starting_time = starting_time[i])
            route_cost = fitness.route_cost()
            #print("route "+ str(i+1) + " duration cost = " + str(route_duration))
            total_duration += route_duration
            total_route_cost += route_cost

        #print("total duration time = " + str(total_duration) + "total distance = " + str(total_route_cost))
        return [total_duration, total_route_cost]
    
    @classmethod
    def sequence_evaluation(cls, sequence, sequence_key, instance_name = Instance.name):
        starting_time = Instance.starting_time[instance_name][sequence_key]
        total_duration = 0
        total_route_cost = 0
        
        fitness

class Gene:
    def __init__(self, client_number, vehicle_number):
        self.client_number = client_number
        self.vehicle_number = vehicle_number
    
    def __repr__(self):
        return "client " + str(self.client_number) + " --> vehicle " + str(self.vehicle_number)

class Individual:
    def __init__(self, number_of_clients = int(Instance.number_of_services / 2) , number_of_vehicles = Instance.number_of_vehicles):
        #genes
        loop = True
        while loop:
            genes = []
            for i in range(number_of_clients):
                client = i + 1
                vehicle = random.randint(1, number_of_vehicles)
                gene = Gene(client, vehicle)
                genes.append(gene)            
            loop = False
            for i in range(1, number_of_vehicles + 1):
                if i not in Individual.vehicles_from_genes(genes):
                    loop = True
        self.genes = genes
        
        #sequences
        vertices = Instance.vertices
        sequences = Utils.format_individual(self)
        for i in range(len(sequences)):
            #i+1 = vehicle number = sequence key
            sequence_key = i + 1
            clients = sequences[sequence_key] 
            vertices = []
            for j in clients:
                origin = j
                destination = int(j+Instance.number_of_services / 2)
                vertices.append(Instance.get_vertice(origin))
                vertices.append(Instance.get_vertice(destination))
            #print("1: " + str(Fitness(vertices).route_distance()))
            sequence = self.best_sequence(vertices, sequence_key)
            #print(sequence)
            sequences[sequence_key] =  [Instance.depot] + sequence + [Instance.depot]
        self.sequences = sequences
    
    @classmethod
    def vehicles_from_genes(cls, genes):
        vehicles = []
        for i in range(len(genes)):
            gene = genes[i]
            vehicles.append(gene.vehicle_number)
        return vehicles
    
    
    def show_sequences(self):
        output = {}
        for i in range(len(self.sequences)):
            output[i + 1] = []
            for vertice in self.sequences[i+1]:
                output[i + 1].append(vertice.number)
        return output
        
    def best_sequence(self, vertices, sequence_key):
        #find the best feasible sequence based on tabu search
        sequence = vertices #initial solution
        sequence_length = len(sequence)
        tabu_time = 3
        i = sequence_length**2
        tabu_list = [[0]*sequence_length]*sequence_length
        best_sequence = sequence
        best_value = Fitness(sequence).route_distance()
        #iterative algorithm
        while i > 0:
            #print(sequence)
            #neighbouring by permutation
            for j in range(1, sequence_length - 1):
                for k in range(1, sequence_length - 1):
                    if tabu_list[j][k] <= 0:
                        temp = sequence[j]
                        sequence[j] = sequence[k]
                        sequence[k] = temp
                        if not Individual.isValid(sequence, sequence_key):
                            temp = sequence[j]
                            sequence[j] = sequence[k]
                            sequence[k] = temp
                        
                        #check if sequence is the best, then update best and tabu_list
                        sequence_value = Fitness(sequence).route_distance()
                        if (tabu_list[j][k] <= 0) and (sequence_value < best_value):
                            best_sequence = sequence
                            best_value = sequence_value
                            #update tabu list
                            for a in range(len(tabu_list)):
                                for b in range(len(tabu_list[a])):
                                    if tabu_list[a][b] -1 >=0:
                                        tabu_list[a][b] -= 1
                            tabu_list[j][k] = tabu_time
            
            #update tabu list
            sequence = best_sequence
            i -= 1
            return best_sequence
    
    @classmethod
    def isValid(cls, sequence, sequence_key):
        capacity = 0
        for i in range(len(sequence)):
            if sequence[i].service_nature == 1:
                origin = sequence[i]
                destination_number = origin.number + int(Instance.number_of_services / 2)
                destination = Instance.get_vertice(destination_number)
            elif sequence[i].service_nature == -1:
                destination = sequence[i]
                origin_number = destination.number - int(Instance.number_of_services / 2)
                origin = Instance.get_vertice(origin_number)
            #print("origin = {} destination = {}".format(origin.number, destination.number))
            #pickup before delivery
            if sequence.index(destination) < sequence.index(origin):
                #print("pickup after delivery")
                return False
            
            #service 1 + trajet + service 2
            if (i < len(sequence)-1):
                #first_service_duration = sequence[i].sevice_time_duration
                #route_distance = Fitness([sequence[i], sequence[i+1]]).route_distance()
                second_service_starting_time = Fitness(sequence[:i+2]).route_duration(starting_time = Instance.starting_time[Instance.name][sequence_key - 1])
                if second_service_starting_time > sequence[i+1].service_later_time:
                    return False
            
            #maximum ride time
            origin_key = sequence.index(origin)
            destination_key = sequence.index(destination)
            origin_starting_time = Fitness(sequence[:origin_key]).route_duration(starting_time = Instance.starting_time[Instance.name][sequence_key - 1])
            destination_starting_time = Fitness(sequence[:destination_key]).route_duration(starting_time = Instance.starting_time[Instance.name][sequence_key - 1])
            if (destination_starting_time - origin_starting_time) > Instance.maximum_ride_time:
                return False
            
            #capacity
            capacity += sequence[i].service_nature
            if capacity > Instance.vehicle_capacity:
                return False
            
        return True
    
    def set_sequences(self, sequences):
        for i in range(len(sequences)):
            self.sequences[i+1] = sequences[i]
    
    @classmethod
    def crossover(cls, parent_1, parent_2):
        #genes
        individual = Individual()
        genes = parent_1.genes[:int(len(parent_2.genes)/2)] + parent_2.genes[int(len(parent_1.genes)/2):]
        loop = True
        while loop:
            loop = False
            for i in range(1, Instance.number_of_vehicles + 1):
                if i not in Individual.vehicles_from_genes(genes):
                    gene_indice = random.randint(0, len(genes) - 1)
                    genes[gene_indice].vehicle_number = i
                    loop = True
        #mutation
        i = random.randint(0, len(genes) - 1)
        j = random.randint(0, len(genes) - 1)
        temp = genes[i].vehicle_number
        genes[i].vehicle_number = genes[j].vehicle_number
        genes[j].vehicle_number = temp
        individual.genes = genes
    
        #sequences
        vertices = Instance.vertices
        sequences = Utils.format_individual(individual)
        for i in range(len(sequences)):
            #i+1 = vehicle number = sequence key
            sequence_key = i + 1
            clients = sequences[sequence_key] 
            vertices = []
            for j in clients:
                origin = j
                destination = int(j+Instance.number_of_services / 2)
                vertices.append(Instance.get_vertice(origin))
                vertices.append(Instance.get_vertice(destination))
            #print("1: " + str(Fitness(vertices).route_distance()))
            sequence = individual.best_sequence(vertices, sequence_key)
            #print(sequence)
            sequences[sequence_key] =  [Instance.depot] + sequence + [Instance.depot]
        individual.sequences = sequences
    
        
        return individual
    
    def __repr__(self):
        if len(self.genes) > 0:
            result = ""
            formatted_individual = Utils.format_individual(self)
            for key in formatted_individual:
                line = "Vehicle " + str(key) + " : " + str(formatted_individual[key]) + "\n"
                result += line
        else:
            result = "Empty individual"
        return result

class Utils:
    @classmethod
    def format_individual(cls, individual):
        solution = {}
        for i in range(len(individual.genes)):
            client = individual.genes[i].client_number
            vehicle = individual.genes[i].vehicle_number
            if vehicle in solution:
                solution[vehicle].append(client)
            else:
                solution[vehicle] = [client]
        return collections.OrderedDict(sorted(solution.items()))
    
    @classmethod
    def current_time(cls):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Temps actuel = ", current_time)

main_program = 1
while(main_program <= 20):
    
    print("<-- start execution {} -->".format(main_program))
    Utils.current_time()
    # step 1: initial population
    population_size = 50
    population = []
    maximum_generation = 50

    for i in range(population_size):
        individual = Individual()
        population.append(individual)
    
    # step 2: loop-generations
    parent_1 = population[0]
    parent_2 = population[1]

    print(parent_1.show_sequences(), Fitness.individual_evaluation(parent_1))
    print(parent_2.show_sequences(), Fitness.individual_evaluation(parent_2))


    for cpt in range(maximum_generation):
        #print(cpt)
        #population evaluation and parents detection
        for i in range(population_size):
            individual = population[i]
            fitness = Fitness.individual_evaluation(individual)
            if fitness[0] < Fitness.individual_evaluation(parent_1)[0]:
                parent_2 = parent_1
                parent_1 = individual
        
        # step 3: new population: crossover and mutation
        population = [parent_1, parent_2]
        for j in range((population_size - 2)):
            population.append(Individual.crossover(parent_1, parent_2))

    #end loop-generations

    for i in range(population_size):
        individual = population[i]
        fitness = Fitness.individual_evaluation(individual)
        if fitness[0] < Fitness.individual_evaluation(parent_1)[0]:
            parent_2 = parent_1
            parent_1 = individual


    print(parent_1.show_sequences(), Fitness.individual_evaluation(parent_1))
    print(parent_2.show_sequences(), Fitness.individual_evaluation(parent_2))
    Utils.current_time()
    print("<-- end execution {} -->".format(main_program))
    main_program += 1
