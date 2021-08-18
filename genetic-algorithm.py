import numpy as np, random, operator, pandas as pd, matplotlib.pyplot as plt

class Instance:
    number_of_vehicles = None
    number_of_services = None
    vehicle_capacity = None
    maximum_ride_time = None
    depot = None
    vertices = []
    
    @classmethod
    def read(cls, instance_path = 'instances/pr01.txt'):
        cls.vertices = []
        with open(instance_path, 'r') as f:
            file_content = f.readlines()[2:]
            
            datas = file_content[2:]
            
            #general information
            instance_description = file_content[0]
            instance_description = instance_description.split()
            cls.number_of_vehicles = instance_description[0]
            cls.number_of_services = instance_description[1]
            cls.vehicle_capacity = instance_description[2]
            cls.maximum_ride_time = instance_description[3]
            
            #depot
            depot = file_content[1]
            depot = depot.split()
            cls.depot = Vertice(number = depot[0], x_coordinate = depot[1], y_coordinate = depot[2], service_time_duration = depot[3], service_nature = depot[4], service_early_time = depot[5], service_later_time = depot[6])
            
        for data in datas:
            data = data.split()
            vertice = Vertice(number = depot[0], x_coordinate = depot[1], y_coordinate = depot[2], service_time_duration = depot[3], service_nature = depot[4], service_early_time = depot[5], service_later_time = depot[6])
            cls.vertices.append(vertice)

class Vertice:
    def __init__(self, number, x_coordinate, y_coordinate, service_time_duration, service_nature, service_early_time, service_later_time):
        self.number = number
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.service_time_duration = service_time_duration
        self.service_nature = service_nature
        self.service_early_time = service_early_time
        self.service_later_time = service_later_time
        self.vehicle_arrival_time = None
        self.departure_time = None
        self.begin_service_time = None
    
    def distance(self, vertice):
        x_distance = abs(self.x_coordinate - vertice.x_coordinate)
        y_distance = abs(self.y_coordinate - vertice.y_coordinate)
        distance = np.sqrt((x_distance**2) + (y_distance**2))
        return distance
    
    def __repr__(self):
        return "(" + str(self.x_coordinate) + ", " + str(self.y_coordinate) + ")"

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0
    
    def route_distance(self):
        if self.distance == 0:
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
    
    def route_fitness(self):
        if self.fitness == 0:
            return None#to do
    
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

class Gene:
    def __init__(self, client_number, vehicle_number):
        self.client_number = client_number
        self.vehicle_number = vehicle_number
    
    def __repr__(self):
        return "client " + str(self.client_number) + " --> vehicle " + str(self.vehicle_number)

class Individual:
    def __init__(self, number_of_clients, number_of_vehicles):
        individual = []
        for i in range(number_of_clients):
            client = i + 1
            vehicle = random.randint(1, number_of_vehicles)
            gene = Gene(client, vehicle)
            individual.append(gene)
        self.genes = individual
    
    def __repr__(self):
        client_string = ""
        vehicle_string = ""
        if len(self.genes) > 0:
            result = ""
            for i in range(len(self.genes)):
                result += "| C" + str(self.genes[i].client_number) + " --> V" + str(self.genes[i].vehicle_number) + " |"
        else:
            result = "Empty individual"
        return result



#TEST
Instance.read()
print(Instance.maximum_ride_time)

#To do
#Verticle.* = None
