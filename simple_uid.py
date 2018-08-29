class _SimpleUIDSingleton:
    def __init__(self):
        self.last_id = -1
    
    def get_id(self):
        self.last_id += 1
        return self.last_id
    
_simple_uid_singleton = None

def SimpleUID():
    global _simple_uid_singleton
    if _simple_uid_singleton == None:
        _simple_uid_singleton = _SimpleUIDSingleton()
    
    return _simple_uid_singleton
    