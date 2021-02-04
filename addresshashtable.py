class AddressHashTable:
    # This will hold all of the relevant pointers for each package so that the packages can
    def __init__(self, initial_value=10):
        # Constructor
        self.table = []
        for i in range(initial_value):
            self.table.append([])

    def insert(self, item):# O(1) average time to complete
        # will insert each package attribute by hashing then inserting a pointer
        # compute hash lookup from id
        bucket = hash(item.address) % len(self.table)
        bucket_list = self.table[bucket]
        if item not in bucket_list:
            bucket_list.append(item)

    def search(self, item):# O(1) average time to complete
        # insert package into
        bucket = hash(item.address) % len(self.table)
        bucket_list = self.table[bucket]
        if item in bucket_list:
            item_index = bucket_list.index(item)
            return bucket_list[item_index]
        else :
            return None

    def search_by_address(self, address_string):# O(1) average time to complete
        bucket = hash(address_string) % len(self.table)
        bucket_list = self.table[bucket]
        for item in bucket_list:
            # each bucket should at most only have a few addresses,
            # but worst case it could contain all addresses
            #iterate through the bucket and return the item
            if item.address == address_string:
                item_index = bucket_list.index(item)
                return bucket_list[item_index]
        # return none if not found
        return None

    def remove(self, item):
        self.table.remove(hash(item.address) % len(self.table))
        return None

    def __str__(self):
        for i in self.table:
            print(i)
