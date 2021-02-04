from datetime import datetime
from enum import Enum
class Package:
    def __init__(self, id, address,deadline, mass, notes, delivered=False): # O(11) 11 variables per object
        self.id = id
        self.address = address # Should be Location object pointer

        if deadline == "EOD":
            self.deadline = deadline
        else:
            self.deadline = datetime.strptime(deadline, '%I:%M %p')
        self.mass = mass
        self.notes = notes
        self.delivered = delivered # boolean defaults to False on creation
        self.delivery_time = None
        self.delivered_by = None
        self.picked_up_time = None
        self.status = PackageStatus(0)


    def get_status_at_time(self, time):
        time_format = "%I:%M %p"
        if time < self.picked_up_time:
            return "Package: "+ str(self.id)+" at Hub"
        elif time > self.picked_up_time and time < self.delivery_time:
            return "Package: "+ str(self.id)+ " on vehicle "+ self.delivered_by + " for delivery "+ " picked up at: "+ self.picked_up_time.strftime(time_format)
        elif time > self.delivery_time:
            return "Package: "+ str(self.id)+ " delivered at "+ self.delivery_time.strftime(time_format) + " by "+ self.delivered_by
        else:
            return "Package: " + str(self.id)+" at Hub"
    def get_status_between_times(self, start, end):
        # this will build a string with relative data
        # then return a string of said data from package+
        id = str(self.id)
        if self.delivery_time < start:
            # package was already delivered
            return "Package id: " + id + " was already delivered"
        if self.delivery_time > start and self.delivery_time < end:
            # package was delivered within the time frame
            return "Package id: " + id + " was delivered at " + self.delivery_time.strftime('%I:%M %p') + " by " + self.delivered_by
        if self.picked_up_time < start:
            # package was picked up already and on truck
            return "Package id: " + id + " is on truck: " + self.delivered_by + " Picked up at: " + self.picked_up_time.strftime(
                '%I:%M %p')
        if self.picked_up_time > start and self.picked_up_time < end:
            # package was picked up within the time frame but not delivered
            return "Package id: " + id + " was picked up at " + self.picked_up_time.strftime('%I:%M %p') + " by " + self.delivered_by
        if self.picked_up_time >= end:
            # package is still at hub
            return "Package id: " + id + " is still at hub"


    def get_deadline(self):
        if isinstance(self.deadline, datetime):
            return self.deadline.strftime("%I:%M %p")
        else:
            return self.deadline
    def pick_up_package(self, truck):
        self.status = PackageStatus(1)# O(1)
        self.picked_up_time = truck.current_time # O(1)
        self.delivered_by = truck.name # O(1)

    def deliver_package(self, truck):
        # set status and update delivery time
        self.status = PackageStatus(2)
        self.delivered = True
        self.delivery_time = truck.current_time
        self.delivered_by = truck.name

        print("package id :", self.id, "delivered at", self.delivery_time.strftime('%I:%M %p'),"by",self.delivered_by)




    def __str__(self):
        delivery_addy = self.address.address # = "%s, %s, %s %s" % (self.address, self.city, self.state, self.zip)
        outstr = "PackageID: %s | Address: %s Notes: %s Deadline: %s" % (self.id, delivery_addy, self.notes, self.get_deadline())
        return(outstr + " delivered at : " + self.delivery_time.strftime('%I:%M %p') + " by " + self.delivered_by)


class PackageStatus(Enum):
    ATHUB = 0
    ENROUTE = 1
    DELIVERED = 2


#
