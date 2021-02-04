import csv
import re
from datetime import datetime
from addresshashtable import AddressHashTable
from location import *
from package import Package



def check_if_near_hub(truck, start, address_map):
    # check if close to hub
    DISTANCE_THRESHOLD = 3.0
    AVAILABLE_PACKAGE_THRESHOLD = 3
    FINAL_SCORE = 0
    if truck.current_location == start:
        return False
    else:
        dist_to_hub = address_map.edge_weights[(truck.current_location,start)]
    package_space_on_truck = 16 - truck.get_package_count()
    if dist_to_hub <= DISTANCE_THRESHOLD:
        FINAL_SCORE += 1
    if package_space_on_truck >= AVAILABLE_PACKAGE_THRESHOLD:
        FINAL_SCORE += 1

    if FINAL_SCORE == 2:
        return True
    else:
        return False

def load_packages(filename, hash_table):
    file = open(filename)
    output = []
    for line in file:
        line_sectioned = line.split(',')
        id = int(line_sectioned[0])
        address = hash_table.search_by_address(line_sectioned[1])
        # city = line_sectioned[2]
        # state = line_sectioned[3]
        # zip = line_sectioned[4]
        deadline = line_sectioned[5]
        mass = int(line_sectioned[6])
        if line_sectioned[7][:5] == "\"Must":
            notes = ",".join(line_sectioned[7:]).strip('"')
        else:
            notes = line_sectioned[7].strip()
        output.append(Package(id, address, deadline, mass, notes))
    return output

def load_addresses(filename): # SpaceTime Complexity: O(n*c) == O(n)
    # Load addresses into weighted graph
    output = CityMap()
    # header row
    header = []
    # create hash table
    hash_table = AddressHashTable(27) # 0(n)
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        row_count = 0
        for row in csv_reader: # SpaceTime Complexity: O(n) linear loop grows with data size
            # add locations to CityMap Graph
            if row_count == 0:
                for item in row: # O(c) constant loop col number stays the same even as data size grows
                    item = item.split('\n') # SpaceTime Complexity: O(n) according to documentation
                    try:
                        location = Location(item[0],item[1]) # SpaceTime Complexity: O(n)
                        output.add_location(location) # SpaceTime Complexity: O(1)
                        # to be referenced with the column counter i.e column 2 = row 1
                        header.append(location) # SpaceTime Complexity: O(1)
                        # print("location added", location.address)
                    except IndexError:
                        # expected Index error while parsing header line
                        # but do nothing, continue processing
                        pass
                row_count+=1
            else:
                # add distances to cityMap Graph
                for col in range(len(row)): # O(m) constant loop col number stays the same even as data size grows
                    if col > 1:
                        # start processing data from 2 onward
                        row_location = header[row_count-1] # SpaceTime Complexity: O(1)
                        col_location = header[col-2] # SpaceTime Complexity: O(1)
                        distance = 0.0 # SpaceTime Complexity: O(1)
                        if row[col]: # SpaceTime Complexity: O(1)
                            distance = float(row[col]) # SpaceTime Complexity: O(1)
                        if distance != 0.0: #SpaceTime Complexity: O(1)
                            output.add_distance(row_location, col_location, distance) # SpaceTime Complexity: O(1)
                        else:
                            break # breaks if cell is empty to move onto next row
                row_count+=1 # SpaceTime Complexity: O(1) increment row count
    # add all addresses to the hash table
    for i in header:
        hash_table.insert(i)

    return hash_table, output

def travel_time(miles):
    # returns travel time in minutes
    speed = 18 # mph SpaceTime Complexity: O(1)
    return miles / speed * 60 # SpaceTime Complexity: O(1)

def sort_packages_by_deadline(package):
    # for sorting packages by the deadline
    return package.get_deadline()

def select_packages_initial(package_list):
    # selects Packages from main list by criteria then outputs four lists
    avail_packages = [] # holds all packages at Hub that will be available SpaceTime Complexity: O(1)
    truck_1_packages = [] # holds all packages that will be loaded onto Truck 1 SpaceTime Complexity: O(1)
    truck_2_packages = [] # holds all packages that will be loaded onto Truck 1 SpaceTime Complexity: O(1)
    delayed_packages = [] # holds packages that will not be on hub until 9:05 SpaceTime Complexity: O(1)
    wrong_packages = [] # holds packages that have wrong addresses that will need correction SpaceTime Complexity: O(1)
    grouped_package_ids = set()
    only_truck_2_address = set()
    # separate packages by special notes status
    for i in package_list: # SpaceTime Complexity: O(n)
        if i.notes == "Delayed on flight---will not arrive to depot until 9:05 am".strip(): # SpaceTime Complexity: O(n) where n is string length
            # delayed package found
            delayed_packages.append(i) # SpaceTime Complexity: O(1)
        elif i.notes == "Wrong address listed":# SpaceTime Complexity: O(n) where n is string length
            # wrong address found, place in wrong address list
            wrong_packages.append(i)
        elif i.notes[:22]=="Must be delivered with": # O(k) where k is string length
            # package grouping found
            re_note_group = r"^[A-Za-z\s]*([0-9]{1,2}),\s?([0-9]{1,2})" # SpaceTime Complexity: O(1)
            m = re.search(re_note_group, i.notes) # SpaceTime Complexity: O(n) where n is string length
            # pull package_id from list
            first_package = int(m.group(1)) # SpaceTime Complexity: O(1)
            second_package = int(m.group(2)) # SpaceTime Complexity: O(1)
            # add grouped ids to one list to load onto a truck
            grouped_package_ids.add(i.id) #SpaceTime Complexity: O(1) average
            grouped_package_ids.add(first_package) # SpaceTime Complexity: O(1) average
            grouped_package_ids.add(second_package) # SpaceTime Complexity: O(1) average
            avail_packages.append(i) #SpaceTime Complexity: O(1)

        elif i.notes == "Can only be on truck 2":
            # package found that must be on truck 2
            truck_2_packages.append(i)
            only_truck_2_address.add(i.address)
        else :
            # all other packages can just be loaded into available packages
            avail_packages.append(i)
    # all packages available should be in this list
    avail_packages.sort(key=sort_packages_by_deadline)
    count = 0

    items_to_remove = []
    for i in avail_packages: # SpaceTime Complexity: O(n) for items in avail_packages
        if i.address in only_truck_2_address and len(truck_2_packages) < 16:
            items_to_remove.append(avail_packages.index(i)) # SpaceTime Complexity: O(n) where n is num of avail_packages
            truck_2_packages.append(i) # SpaceTime Complexity: O(1)

    if items_to_remove: # SpaceTime Complexity: O(1)
        for i in sorted(items_to_remove, reverse=True):# sorting is SpaceTime Complexity: O(n log n) worst case is O(n) average is SpaceTime Complexity: O(1)
            # remove packages
            del avail_packages[i]# SpaceTime Complexity: O(n)

    items_to_remove = [] # SpaceTime Complexity: O(1)
    group_addresses = set() # SpaceTime Complexity: O(1)

    # add grouped items to truck 2
    for i in avail_packages: # SpaceTime Complexity: O(n)
        if i.id in grouped_package_ids and len(truck_2_packages) < 16: # O(1+1)
            # store index for deletion later
            items_to_remove.append(avail_packages.index(i))# SpaceTime Complexity: O(n)
            truck_2_packages.append(i) # SpaceTime Complexity: O(1)
            group_addresses.add(i.address) # SpaceTime Complexity: O(1)

    # delete items
    if items_to_remove: #SpaceTime Complexity: O(1)
        for i in sorted(items_to_remove, reverse=True): #SpaceTime Complexity: O(n log n) + O(n)
            # remove packages
            del avail_packages[i]
    # empty list
    items_to_remove = [] # SpaceTime Complexity: O(1)
    # add packages that match grouped package addresses to truck_2
    for i in avail_packages: # SpaceTime Complexity: O(n)
        if i.address in group_addresses and len(truck_2_packages) < 16: # SpaceTime Complexity: O(1) + O(1)
            truck_2_packages.append(i)# SpaceTime Complexity: O(1)
            items_to_remove.append(avail_packages.index(i))# SpaceTime Complexity: O(1) + O(n)
        elif len(truck_2_packages) >= 16: # SpaceTime Complexity: O(1)
            break

    if items_to_remove: # SpaceTime Complexity: O(n)
        for i in sorted(items_to_remove, reverse=True): # SpaceTime Complexity: O(n log n) + O(n)
            # remove packages
            del avail_packages[i] # SpaceTime Complexity: O(n)

    # sort available packages by deadline in place
    avail_packages.sort(key=sort_packages_by_deadline)

    # while packages can still be added to the trucks
    while (len(truck_1_packages) < 16) or (len(truck_2_packages) < 16): # O(32) since the packages are added each loop
        # switches back and forth between trucks
        if (count % 2 == 0):
            # TRUCK 1
            if (len(truck_1_packages) < 16) and avail_packages:# SpaceTime Complexity: O(1) + SpaceTime Complexity: O(1)
                # add packages to truck_1
                # check for packages and if first package has a time deadline
                if isinstance(avail_packages[0].deadline, datetime): # Assuming this is SpaceTime Complexity: O(1)
                    # pull first package with deadline
                    this_package = avail_packages.pop(0) # SpaceTime Complexity: O(1)
                    # add this package to truck_1 package list
                    truck_1_packages.append(this_package) # SpaceTime Complexity: O(1)
                    # check for other addresses that match this package address and add to truck
                    idxs = [] # SpaceTime Complexity: O(1)
                    for i in avail_packages: # SpaceTime Complexity: O(n)
                        # if package addresses match
                        if i.address == this_package.address and len(truck_1_packages) < 16: # SpaceTime Complexity: O(1) + O(1)
                            # add to truck
                            truck_1_packages.append(i) # SpaceTime Complexity: O(1)
                            # store index in package_list
                            idxs.append(avail_packages.index(i))# SpaceTime Complexity: O(1) + O(n)
                    # delete all same addresses from available packages
                    for i in sorted(idxs, reverse=True): # SpaceTime Complexity: O(n log n) * O(n)
                        del avail_packages[i]
                else:
                    # packages have EOD deadline
                    this_package = avail_packages.pop(0)
                    truck_1_packages.append(this_package)
                    idxs = []
                    for i in avail_packages:
                        if i.address == this_package.address and len(truck_1_packages) < 16:
                            # add to truck
                            truck_1_packages.append(i)
                            idxs.append(avail_packages.index(i))
                    for i in sorted(idxs, reverse=True):
                        del avail_packages[i]
        else :
            # TRUCK 2 - same procedure as truck 1
            if (len(truck_2_packages) < 16) and avail_packages:
                # add packages to truck_2
                # check for packages and if first package has a time deadline
                if isinstance(avail_packages[0].deadline, datetime):
                    # pull first package with deadline
                    this_package = avail_packages.pop(0)
                    # add this package to truck_2 package list
                    truck_2_packages.append(this_package)
                    # check for other addresses that match this package and add to truck
                    idxs = []
                    for i in avail_packages:
                        if i.address == this_package.address and len(truck_2_packages) < 16:
                            # add to truck
                            print("adding similar initial package to truck 2", i.address.address)
                            truck_2_packages.append(i)
                            idxs.append(avail_packages.index(i))
                    for i in sorted(idxs, reverse=True):
                        del avail_packages[i]
                else:
                    # packages have EOD deadline
                    this_package = avail_packages.pop(0)
                    truck_2_packages.append(this_package)
                    idxs = []
                    for i in avail_packages:
                        if i.address == this_package.address and len(truck_2_packages) < 16:
                            # add to truck
                            truck_2_packages.append(i)
                            idxs.append(avail_packages.index(i))
                    for i in sorted(idxs, reverse=True):
                        del avail_packages[i]

        # increment count
        count += 1
    # sort both package lists by deadline
    truck_1_packages.sort(key=sort_packages_by_deadline) # SpaceTime Complexity: O(n log n)
    truck_2_packages.sort(key=sort_packages_by_deadline) # SpaceTime Complexity: O(n log n)

    # return all package lists
    return avail_packages, truck_1_packages, truck_2_packages, delayed_packages, wrong_packages

def find_next_package(packages, truck, address_map):
    # O(16) worst case since package list will be from truck itself
    # package list should be sorted by deadline when passed into function
    # early morning packages get priority delivery regardless of order
    early_time = datetime.strptime("09:00 AM", "%I:%M %p")
    if packages[0].deadline == early_time:
        return packages[0], 0

    min_dist = 1000.0 # SpaceTime Complexity: O(1)
    next_package = None # SpaceTime Complexity: O(1)
    index = -1 # SpaceTime Complexity: O(1)
    # for each package in packages
    for i in range(len(packages)): # SpaceTime Complexity: O(16)
        addy = packages[i].address # SpaceTime Complexity: O(1)
        # only if the addy is not current
        # otherwise the edge weight will not be found
        if addy != truck.current_location: #SpaceTime Complexity: O(1)
            dist = address_map.edge_weights[(truck.current_location, addy)] # SpaceTime Complexity: O(1) average
        # if the distance is less than previously stored min_dist
        if dist < min_dist: # SpaceTime Complexity: O(1)
            # add that distance to the min for further checking
            min_dist = dist # SpaceTime Complexity: O(1)
            # set the next package to this package, jic
            next_package = packages[i] # SpaceTime Complexity: O(1)
            # update the index of that package
            index = i # SpaceTime Complexity: O(1)
    # return the closest address found in the package
    return next_package, index
