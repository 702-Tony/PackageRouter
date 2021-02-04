###  Name : Anthony Adams
###  Student ID : 000968458
###  C950 Performance Assessment
from hashtable import HashTable
from helpers import *
from truck import Truck
from datetime import timedelta

if __name__ == "__main__":
    # start the program
    print("Starting WGUPS Package Router")
    # create trucks
    truck_1 = Truck("Truck 1") # constant time t(1)
    truck_2 = Truck("Truck 2") # constant time t(1)
    print("Loading City Map")
    # load in addresses into map and hash table
    address_hash_table, address_map = load_addresses("distance_table.csv")
    # sort packages by deadline first
    print("Readying Packages")
    main_list = load_packages("package_list.csv", address_hash_table)
    package_list = sorted(main_list, key=sort_packages_by_deadline) # SpaceTime Complexity: O(n*log(n)) based on python documentation.
    # Python uses a modified mergesort called timsort. requires a temp array with max n/2 pointers for the operation

    # select initial packages to be loaded onto truck for delivery first thing in the morning
    avail_packages, truck_1_packages, truck_2_packages, delayed_packages, wrong_packages = select_packages_initial(package_list)

    # get starting location from hash table
    starting_location = address_hash_table.search_by_address("4001 South 700 East,".strip())

    # Trucks start at HUB
    truck_1.current_location = starting_location
    truck_2.current_location = starting_location

    # format for printing datetime objects
    TIME_FORMAT = '%I:%M %p'

    # This What time trucks will leave the hub in the morning
    start_time = datetime.strptime("08:00 AM", TIME_FORMAT)

    # late packages will hit the hub at this time
    late_package_ready_time = datetime.strptime("09:05 AM", TIME_FORMAT)

    # What time the addresses will be expected to be fixed on the packages
    wrong_address_fix_time = datetime.strptime("10:20 AM", TIME_FORMAT)

    # Main Loop for package delivery
    truck_1.current_time = start_time
    truck_2.current_time = start_time

    # counts packages being delivered
    total_packages_delivered = 0

    # Load Packages onto truck
    for i in truck_1_packages: # O(16)
        truck_1.load_package(i)
    for i in truck_2_packages: # O(16)
        truck_2.load_package(i)
    # bool to check if the late packages have been picked up
    late_packages_picked_up = False

    # bool to check if all packages have been delivered to break out of the loop
    all_delivered = False

    while(not all_delivered): # SpaceTime Complexity: O(n^3) - This will deliver all packages throughout the while loop and subsequent for loops
        # for updating the wrong address listed packages and adding them to the avail
        #O(1) + O(1) + O(1)
        if wrong_packages and (truck_1.current_time >= wrong_address_fix_time and truck_2.current_time >= wrong_address_fix_time):
            # fix the address on the package new_location
            address_update = address_hash_table.search_by_address("410 S State St")# SpaceTime Complexity: O(1) Average
            wrong_packages[0].address = address_update # SpaceTime Complexity: O(1)
            # remove from wrong_packages list and add to avail_packages
            avail_packages.append(wrong_packages.pop()) # SpaceTime Complexity: O(1) + O(1)
            print("wrong address fix incoming.")


        if not late_packages_picked_up and truck_1.current_time >= late_package_ready_time:
            # Have truck_1 head back and pick_up the late packages
            #####################
            # head back to hub
            trip_distance = address_map.edge_weights[(truck_1.current_location, starting_location)] # SpaceTime Complexity: O(1) Average
            truck_1.distance_traveled += trip_distance # SpaceTime Complexity: O(1)
            truck_1.current_time += timedelta(minutes = (travel_time(trip_distance))) # SpaceTime Complexity: O(1)
            truck_1.current_location = starting_location # SpaceTime Complexity: O(1)
            #####################
            # store package index from delayed to delete later
            tbdeleted = []
            # Add packages to available package queue
            for i in delayed_packages:# SpaceTime Complexity: O(n) worst case, in this case it is O(4)
                avail_packages.append(i)
                # store index to delete later
                tbdeleted.append(delayed_packages.index(i))
            # delete from unavailable packages list
            for i in sorted(tbdeleted, reverse=True):
                del delayed_packages[i]
            # sort packages by deadline again...
            avail_packages.sort(key=sort_packages_by_deadline)# SpaceTime Complexity: O(n*log n)

            while truck_1.get_package_count() < 16: # SpaceTime Complexity: O(16)*O(n^2) Worst case
                # load additional packages onto truck 1 if it has space
                if avail_packages:# if there are packages available # SpaceTime Complexity: O(1)
                    new_package = avail_packages.pop(0) # always removing one from avail_packages
                    truck_1.load_package(new_package)
                    tbdeleted = []
                    for i in avail_packages: # SpaceTime Complexity: O(n)
                        if (i.address == new_package.address) and truck_1.get_package_count() < 16:
                            # grab more packages with the same address as the ones you are adding if you can
                            # save indexes so the packages can be deleted from the avail packages list
                            tbdeleted.append(avail_packages.index(i)) # SpaceTime Complexity: O(n) + O(1)
                            truck_1.load_package(i)
                        elif truck_1.get_package_count() >= 16: # SpaceTime Complexity: O(2)
                            break # truck full! break from for loop
                    # delete all packages added to truck with same address from avail packages
                    for i in sorted(tbdeleted, reverse=True): # SpaceTime Complexity: O(m)+O(m log m)
                            del avail_packages[i]
                else:
                    break
            truck_1.packages.sort(key=sort_packages_by_deadline)
            late_packages_picked_up = True

        # Truck 1 - If there are priority packages to be delivered
        # Priority Packages are any packages with deadlines, i.e. 9:00 am or 10:30 am
        if truck_1.priority_packages: # SpaceTime Complexity: O(16) worst case
            # Find next package to deliver
            # this finds the nearest location next in all packages
            truck_1_tbd, remove_index = find_next_package(truck_1.priority_packages, truck_1, address_map) #SpaceTime Complexity: O(n)
            del truck_1.priority_packages[remove_index] # SpaceTime Complexity: O(n)


            #####################
            # drive to location
            trip_distance = address_map.edge_weights[(truck_1.current_location, truck_1_tbd.address)] #SpaceTime Complexity: O(1) average
            # update truck distance value
            truck_1.distance_traveled += trip_distance # SpaceTime Complexity: O(1)
            # update current_location and delivery time on truck
            truck_1.current_time += timedelta(minutes=(travel_time(trip_distance))) # SpaceTime Complexity: O(1)
            truck_1.current_location = truck_1_tbd.address # SpaceTime Complexity: O(1)
            #####################

            total_packages_delivered += 1 # SpaceTime Complexity: O(1)
            # DELIVER PACKAGE
            truck_1_tbd.deliver_package(truck_1) # SpaceTime Complexity: O(1)
            # check for packages with the same address then deliver package
            pkgs_to_deliver_curr_addy = truck_1.get_pkgs_same_addy(truck_1_tbd)# SpaceTime Complexity: O(16) since packages will only have 16
            for i in pkgs_to_deliver_curr_addy: # SpaceTime Complexity: O(16)
                total_packages_delivered += 1
                i.deliver_package(truck_1)


        elif truck_1.packages:# SpaceTime Complexity: O(16) worst case
            # find next package to deliver
            truck_1_tbd, remove_index = find_next_package(truck_1.packages, truck_1, address_map)
            # delete package from truck packages
            del truck_1.packages[remove_index]

            #####################
            # drive to location
            trip_distance = address_map.edge_weights[(truck_1.current_location, truck_1_tbd.address)]
            # update truck distance value
            truck_1.distance_traveled += trip_distance
            # update current_location and delivery time on truck
            truck_1.current_time += timedelta(minutes=(travel_time(trip_distance)))
            truck_1.current_location = truck_1_tbd.address
            #####################

            # update packages delivered
            total_packages_delivered += 1
            # deliver package
            truck_1_tbd.deliver_package(truck_1)
            # check for packages with the same address
            pkgs_to_deliver_curr_addy = truck_1.get_pkgs_same_addy(
                truck_1_tbd)
            for i in pkgs_to_deliver_curr_addy:
                total_packages_delivered += 1
                i.deliver_package(truck_1)

        else : # SpaceTime Complexity: O(16) worst case
            # head back to hub and pick up more packages
            # add packages to truck_1 if they fit criteria
            if truck_1.current_location == starting_location:
                # if already at hub...
                print(truck_1.name,"checking for/picking up packages at hub...")
                while truck_1.get_package_count() < 16: #SpaceTime Complexity: O(16) worst case
                    # if packages available load onto truck
                    if avail_packages:
                        truck_1.load_package(avail_packages.pop(0)) #SpaceTime Complexity: O(5)
                    else:
                        print("no more packages")
                        break
            else:
                # drive back to hub
                print("heading back to hub...")
                trip_distance = address_map.edge_weights[(truck_1.current_location, starting_location)]# SpaceTime Complexity: O(1)
                truck_1.current_location = starting_location #SpaceTime Complexity: O(1)
                truck_1.current_time += timedelta(minutes=(travel_time(trip_distance))) # SpaceTime Complexity: O(1)
                # Load new Packages that have not been delivered

        ###################
        ###   Truck 2   ###
        ###################
        if truck_2.priority_packages:
            next_package, remove_index = find_next_package(truck_2.priority_packages, truck_2, address_map)
            del truck_2.priority_packages[remove_index]
            truck_2_tbd = next_package
            # !!!! when pulling distance use address_map.edge_weights[(from, to)]
            #####################
            # drive to location
            trip_distance = address_map.edge_weights[(truck_2.current_location, truck_2_tbd.address)]
            # update truck distance value
            truck_2.distance_traveled += trip_distance
            # update current_location and delivery time on truck
            truck_2.current_time += timedelta(minutes=(travel_time(trip_distance)))
            truck_2.current_location = truck_2_tbd.address
            #####################
            # print("t2 delivering package id:", truck_2_tbd.id, "at", truck_2.current_time.strftime(TIME_FORMAT))
            # print(truck_2_tbd.id, "deadline:", truck_2_tbd.get_deadline())

            # set package to delivered and update status
            total_packages_delivered += 1

            truck_2_tbd.deliver_package(truck_2)
            # check for packages with the same address then deliver package
            pkgs_to_deliver_curr_addy = truck_2.get_pkgs_same_addy(
                truck_2_tbd)  # sorted([truck_1.packages.index(x) for x in truck_1.packages if x.address == truck_1.current_location], reverse=True)
            for i in pkgs_to_deliver_curr_addy:
                total_packages_delivered += 1
                i.deliver_package(truck_2)



        elif truck_2.packages:
            # pull package
            next_package, remove_index = find_next_package(truck_2.packages, truck_2, address_map)
            del truck_2.packages[remove_index]

            truck_2_tbd = next_package # truck_2.packages.pop(0)


            #####################
            # drive to location
            trip_distance = address_map.edge_weights[(truck_2.current_location, truck_2_tbd.address)]
            # update truck distance value
            truck_2.distance_traveled += trip_distance
            # update current_location and delivery time on truck
            truck_2.current_time += timedelta(minutes=(travel_time(trip_distance)))
            truck_2.current_location = truck_2_tbd.address
            #####################


            # deliver package
            truck_2_tbd.deliver_package(truck_2)
            total_packages_delivered += 1

            # check for packages with the same address then deliver package
            pkgs_to_deliver_curr_addy = truck_2.get_pkgs_same_addy(truck_2_tbd)
            for i in pkgs_to_deliver_curr_addy:
                total_packages_delivered += 1
                i.deliver_package(truck_2)
        else:
            # head back to start and pick up more packages
            # add packages to truck_2 if they fit criteria
            if truck_2.current_location == starting_location:
                # if already at hub...
                print(truck_2.name,"checking for/picking up packages at hub...")
                while truck_2.get_package_count() < 16:
                    # if packages available load onto truck
                    if avail_packages:
                        truck_2.load_package(avail_packages.pop(0))
                    else:
                        print("no more packages")
                        break
            else:
                # drive back to hub
                print("heading back to hub...")
                trip_distance = address_map.edge_weights[(truck_2.current_location, starting_location)]
                truck_2.current_location = starting_location
                truck_2.current_time += timedelta(minutes=(travel_time(trip_distance)))
                # Load new Packages that have not been delivered

        # Check all packages were delivered
        all_delivered = True
        for i in main_list:# SpaceTime Complexity: O(n)
            if i.delivered == False: # SpaceTime Complexity: O(1)
                all_delivered = False# SpaceTime Complexity: O(1)
                break
    print("total truck 1 distance =", truck_1.distance_traveled)
    print("time finished =", truck_1.current_time.strftime(TIME_FORMAT))
    print("total truck 2 distance =", truck_2.distance_traveled)
    print("time finished =", truck_2.current_time.strftime(TIME_FORMAT))
    print("total_distance for both", truck_1.distance_traveled+truck_2.distance_traveled)
    print("total num packages delivered", total_packages_delivered)

    # create hash Table with id as hash reference
    main_hash_table = HashTable(total_packages_delivered) # creates hash table with 40 buckets
    for i in main_list:
        main_hash_table.insert(i)










    # print("Loading Packages")
    done = False
    option = -1

    # Begin Interface for user
    while(not done):
        # take selections from the user to decide what to do
        while True:
            print("Please make a selection.")
            print("you can look up packages by:")
            print(" " * 5, "1. Search by ID")
            print(" " * 5, "2. Search by Time")
            print(" " * 5, "3. Search by Time and ID")
            print(" " * 5, "4. Search Between two times")
            print(" " * 5, "5. Get Distances Traveled")
            print(" " * 5, "6. See All Package Statuses")
            print(" " * 5, "7. Exit")
            try :
                option = int(input("What would you like to do?  "))
                if option == 1:
                    lookup_id = int(input("Enter ID you would like to look up?  "))
                    lookup_package = main_hash_table.search_by_id(lookup_id)
                    if lookup_package:
                        print(lookup_package)
                    else:
                        print("Sorry. Package ID not found... ")
                elif option == 2:
                    lookup_time = datetime.strptime((input("Enter time(format: HH:MM am) you would like to lookup: ")), TIME_FORMAT)
                    for i in main_list:
                        print(i.get_status_at_time(lookup_time))
                elif option == 3:
                    lookup_id = int(input("Enter ID you would like to lookup"))
                    lookup_time = datetime.strptime(input("Enter time(format: HH:MM am) you would like to lookup: "), TIME_FORMAT)
                    lookup_package = main_hash_table.search_by_id(lookup_id)
                    print(lookup_package.get_status_at_time(lookup_time))
                elif option == 4:
                    start_time = datetime.strptime((input("Enter start time(format: HH:MM am): ")), TIME_FORMAT)
                    end_time = datetime.strptime((input("Enter end time(format: HH:MM am): ")), TIME_FORMAT)
                    if start_time > end_time:
                        print("ERROR: Start time cannot be after end time")
                    else:
                        print("Getting status between", start_time.strftime(TIME_FORMAT), "and", end_time.strftime(TIME_FORMAT))
                        for i in main_list:
                            print(i.get_status_between_times(start_time, end_time))
                elif option == 5:
                    print("total truck 1 distance =", truck_1.distance_traveled)
                    print("total truck 2 distance =", truck_2.distance_traveled)
                    print("total traveled", truck_1.distance_traveled + truck_2.distance_traveled)
                elif option == 6:
                    for i in sorted(package_list, key=lambda l: l.id):
                        print(i)
                elif (option == 7):
                    print("Goodbye :)")
                    done = True
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Sorry that will not work")
