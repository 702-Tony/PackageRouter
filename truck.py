from datetime import datetime
class Truck:
    def __init__(self, name=None):
        self.name = name
        self.packages = []
        self.priority_packages = []
        self.current_location = None
        self.current_time = None
        self.distance_traveled = 0.0

    def load_package(self, package): # O(5)
        if isinstance(package.deadline, datetime): # O(1)
            # if package has set time to be delivered by
            self.priority_packages.append(package)# O(1)
            # priority package added
        else:
            # otherwise package can be delivered end of day
            self.packages.append(package)# O(1)
            # package added
        package.pick_up_package(self) # O(3)

    def get_package_count(self):# O(2)
        # return package counts for both lists
        return len(self.packages) + len(self.priority_packages)# O(1)+O(1)

    def get_pkgs_same_addy(self, package): # O(16) worst case since trucks are never loaded past 16 packages in either list
        # returns all packages on truck with same address to be delivered
        # create list to return
        found_packages = [] # O(1)
        # count backwards both times
        # to not run into index errors
        for i in range(len(self.packages)-1, -1, -1): # O(16) worst case
            if self.packages[i].address == package.address:
                # package found
                found_packages.append(self.packages.pop(i))
        for i in range(len(self.priority_packages)-1, -1, -1): # O(16) worst case
            if self.priority_packages[i].address == package.address:
                # priority package found
                found_packages.append(self.priority_packages.pop(i)) # O(1)
        return found_packages

