class _ObjectUniverseSingleton:

    def __init__(self):
        self.objects = []

    def add_object(self, object):
        self.objects.append(object)
        return self

    def get_objects(self, time_stamp):
        return self.objects

_object_universe_singleton = None

def ObjectUniverse():
    global _object_universe_singleton
    if _object_universe_singleton == None:
        _object_universe_singleton = _ObjectUniverseSingleton()
    
    return _object_universe_singleton
