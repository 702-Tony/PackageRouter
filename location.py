
class Location:
    def __init__(self, location, address): # O(n)
        self.location = location.strip() # O(n) where n equals length of string to remove leading and trailing whitespace
        self.address = address.strip() # o(n) where n equals length of string
    def __str__(self):
        return "%s located at %s" % (self.location, self.address)

class CityMap:
    # Graph for holding edge weights for figuring out distances
    # as well as adjacent stops
    def __init__(self):
        # to find distance map.edge_weights[(from, to)]
        # to find adjacencies = map.adjacency_list[location]
        self.adjacency_list = {}
        self.edge_weights = {}

    def add_location(self, new_location):
        self.adjacency_list[new_location]=[] #O(1)

    def one_way(self, from_loc, to_loc, distance=1.0): # O(1)
        self.edge_weights[(from_loc, to_loc)] = distance# O(1)
        self.adjacency_list[(from_loc)].append(to_loc)# O(1)

    def add_distance(self, location1, location2, distance):
        self.one_way(location1, location2, distance)
        self.one_way(location2, location1, distance)

    def __str__(self):
        return(str(list(self.adjacency_list)))
