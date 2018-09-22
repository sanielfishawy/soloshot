from viewable_object import ViewableObjects

class ObjectUniverse:

    def __init__(self, num_timestamps=1000):
        self.viewable_objects = []
        self.camera = None
        self.tag = None
        self.num_timestamps = num_timestamps

    def add_camera(self, camera):
        self.camera = camera
        self.camera.set_object_universe(self).set_num_timestamps(self.get_num_timestamps())
        return self

    def get_camera(self):
        '''
        :rtype Camera
        '''
        return self.camera

    def set_num_timestamps(self, n):
        self.num_timestamps = n
        for vo in self.viewable_objects:
            vo.set_num_timestamps(self.num_timestamps)
        
        if self.camera != None:
            self.camera.set_num_timestamps(self.num_timestamps)
        return self
    
    def get_num_timestamps(self):
        return self.num_timestamps
            
    def add_viewable_objects(self, viewable_objects):
        if not isinstance(viewable_objects, list):
            viewable_objects = [viewable_objects]

        for obj in viewable_objects:
            obj.set_num_timestamps(self.num_timestamps)

        self.viewable_objects += viewable_objects
        return self

    def get_viewable_objects(self):
        return self.viewable_objects
    
    def get_viewable_objects_as_viewable_objects_class(self):
        return ViewableObjects(viewable_objects=self.get_viewable_objects())

    def clear_viewable_objects(self):
        self.viewable_objects = []
        return self

    def get_num_viewable_objects(self):
        return len(self.viewable_objects)