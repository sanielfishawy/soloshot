class _ObjectUniverseSingleton:

    def __init__(self):
        self.objects = []

    def add_objects(self, objects):
        if not isinstance(objects, list):
            objects = [objects]

        self.objects += objects
        return self

    def get_objects(self, time_stamp):
        return self.objects

    def clear_objects(self):
        self.objects = []
        return self

    def get_num_objects(self):
        return len(self.objects)

_object_universe_singleton = None

def ObjectUniverse():
    global _object_universe_singleton
    if _object_universe_singleton == None:
        _object_universe_singleton = _ObjectUniverseSingleton()
    
    return _object_universe_singleton
