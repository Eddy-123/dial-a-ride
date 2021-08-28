import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt, collections

class Instance:
    number_of_vehicles = None
    number_of_services = None
    vehicle_capacity = None
    maximum_ride_time = None
    depot = None
    vertices = []
    starting_time = {'pr01': [188.54, 148.08, 83.13]}
    name = 'pr01'
    
    @classmethod
    def read(cls, instance_path = 'instances/pr01.txt'):
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
        individual = []
        #genes
        for i in range(number_of_clients):
            client = i + 1
            vehicle = random.randint(1, number_of_vehicles)
            gene = Gene(client, vehicle)
            individual.append(gene)            
        self.genes = individual
    
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
            sequences[sequence_key] = sequence
        self.sequences = sequences
        
    
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
                        if Individual.isValid(sequence, sequence_key):
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
        for i in range(len(sequence)):
            if sequence[i].service_nature == 1:
                origin = sequence[i]
                destination_number = origin.number + int(Instance.number_of_services / 2)
                destination = Instance.get_vertice(destination_number)
            elif sequence[i].service_nature == -1:
                destination = sequence[i]
                origin_number = destination.number - int(Instance.number_of_services / 2)
                origin = Instance.get_vertice(origin_number)
            #pickup before delivery
            if sequence.index(destination) < sequence.index(origin):
                return False
            
            #service 1 + trajet + service 2
            if (i < len(sequence)-1):
                #first_service_duration = sequence[i].sevice_time_duration
                #route_distance = Fitness([sequence[i], sequence[i+1]]).route_distance()
                second_service_starting_time = Fitness(sequence[:i+2]).route_duration(starting_time = Instance.starting_time[Instance.name][sequence_key - 1])
                if second_service_starting_time > sequence[i+1].service_later_time:
                    return False
        return True
    
    def set_sequences(self, sequences):
        for i in range(len(sequences)):
            self.sequences[i+1] = sequences[i]
    
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


# step 1: initial population
individual = Individual()
best = Fitness.individual_evaluation(individual)
for i in range(100000):
    individual = Individual()
    fitness = Fitness.individual_evaluation(individual)
    if best[0] > fitness[0]:
        best = fitness
    print(best)
