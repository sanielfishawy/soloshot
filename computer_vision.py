from simple_uid import SimpleID

class ComputerVision:

    def __init__(self, camera=None):
        self.camera = camera
        self.id_gen = SimpleID(prefix='cv')
        self.init_viewable_object_id_history()
        
    def init_viewable_object_id_history(self):
        self.viewable_object_id_history = [{}] * self.camera.get_num_timestamps()

    def get_viewable_object_id_history(self):
        return self.viewable_object_id_history

    def set_camera(self, camera):
        self.camera = camera
        return self
    
    def get_camera(self):
        return self.camera

    def set_cv_ids_for_all_camera_time(self):
        for timestamp, _ in enumerate(self.camera.get_state_history()):
            self.set_cv_ids_for_objects_at_timestamp(timestamp)

    def set_cv_ids_for_objects_at_timestamp(self, timestamp):
        self.clear_cv_ids_of_out_of_view_objects(timestamp)
        self.set_cv_ids_of_out_of_view_objects(timestamp)

    def clear_cv_ids_of_out_of_view_objects(self, timestamp):
        for ov_obj in self.camera.get_objects_out_view(timestamp):
            self.set_cv_id_for_obj_at_timestamp(ov_obj, timestamp, None)

    def set_cv_ids_of_out_of_view_objects(self, timestamp):
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
            return self.get_cv_id_for_obj_at_timestamp(obj, timestamp)

    def set_cv_id_for_obj_at_timestamp(self, obj, timestamp, cv_id):
            self.get_viewable_object_id_history()[timestamp][obj] = cv_id

    def get_cv_id_for_obj_at_timestamp(self, obj, timestamp):
        return self.get_viewable_object_id_history()[timestamp][obj]
