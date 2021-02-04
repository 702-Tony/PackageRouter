class HashTable:
    def __init__(self, initial_value=10):
        # Constructor
        self.table = []
        for i in range(initial_value):
            self.table.append([])

    def insert(self, item): # O(1) average time to complete
        # will insert each package attribute by hashing then inserting a pointer
        # compute hash lookup from id
        bucket = hash(item.id) % len(self.table)
        bucket_list = self.table[bucket]
        if item not in bucket_list:
            bucket_list.append(item)

    def search(self, item): # O(1) average time to complete
        # insert package into
        bucket = hash(item.id) % len(self.table)
        bucket_list = self.table[bucket]
        if item in bucket_list:
            item_index = bucket_list.index(item)
            return bucket_list[item_index]
        else:
            return None

    def search_by_id(self, id): # O(1) average time to complete
        bucket = hash(id) % len(self.table)
        bucket_list = self.table[bucket]
        for item in bucket_list:
            if item.id == id:
                item_index = bucket_list.index(item)
                return bucket_list[item_index]


        return None


    def remove(self, item):
        self.table.remove(hash(item.id) % len(self.table))