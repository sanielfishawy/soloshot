from simple_uid import SimpleID

class ComputerVision:

    def __init__(self):
        self.id_gen = SimpleID(prefix='cv')
        
    def init_viewable_object_id_history(self):
        self.viewable_object_id_history = [None] * self.camera.get_num_timestamps()

    def get_viewable_object_id_history(self):
        return self.viewable_object_id_history
    
    def set_camera(self, camera):
        self.camera = camera
        self.init_viewable_object_id_history()
        return self
    
    def get_camera(self):
        return self.camera

    def camera_num_timestamps_changed(self):
        self.init_viewable_object_id_history()

    def set_cv_ids_for_all_camera_time(self):
        for timestamp in range(0, self.camera.get_num_timestamps()):
            self.set_cv_ids_for_objects_at_timestamp(timestamp)
        return self

    def set_cv_ids_for_objects_at_timestamp(self, timestamp):
        self.clear_cv_ids_of_out_of_view_objects(timestamp)
        self.set_cv_ids_of_in_view_objects(timestamp)

    def clear_cv_ids_of_out_of_view_objects(self, timestamp):
        for ov_obj in self.camera.get_objects_out_view(timestamp):
            self.set_cv_id_for_obj_at_timestamp(ov_obj, timestamp, None)

    def set_cv_ids_of_in_view_objects(self, timestamp):
        for iv_obj in self.camera.get_objects_in_view(timestamp):
            prev_id = self.get_cv_id_for_object_in_prev_timestamp(iv_obj, timestamp)
            if prev_id == None:
                self.set_cv_id_for_obj_at_timestamp(iv_obj, timestamp, self.id_gen.get_id())
            else:
                self.set_cv_id_for_obj_at_timestamp(iv_obj, timestamp, prev_id)

    def get_cv_id_for_object_in_prev_timestamp(self, obj, timestamp):
        if timestamp == 0:
            return None
        else:
            return self.get_cv_id_for_obj_at_timestamp(obj, timestamp - 1)

    def set_cv_id_for_obj_at_timestamp(self, obj, timestamp, cv_id):
        if self.viewable_object_id_history[timestamp] == None:
            self.viewable_object_id_history[timestamp] = {}
        self.viewable_object_id_history[timestamp][obj] = cv_id

    def get_cv_id_for_obj_at_timestamp(self, obj, timestamp):
        if self.get_viewable_object_id_history() == None or \
           self.get_viewable_object_id_history()[timestamp] == None:
           return None
        else:
           return self.get_viewable_object_id_history()[timestamp][obj]
