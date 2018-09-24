import sys
sys.path.insert(0, '/Users/sani/dev/soloshot')
from object_universe import ObjectUniverse
from camera import Camera
from computer_vision import ComputerVision
from viewable_object import RandomlyMovingObject
from boundary import Boundary
from tk_canvas_renderers.render_orchestrator import RenderOrchestrator

class Demo:

    def __init__(self):

        # Setup physical environment
        self.num_timestamps = 100

        self.camera = Camera() 
        self.camera.set_actual_position((100,300)).\
                    set_gps_position((100,290)).\
                    set_gps_max_error(10).\
                    set_fov_deg(70)
        for timestamp in range(self.num_timestamps):
            self.camera.set_pan_angle_deg(0, timestamp)

        self.cv = ComputerVision()
        self.camera.set_computer_vision(self.cv)

        self.boundary = Boundary([(150, 100), (150, 550), (300, 550), (300, 100)])

        self.viewable_objects = []
        for _ in range(20):
            self.viewable_objects.append(RandomlyMovingObject(boundary=self.boundary))
        
        self.object_universe = ObjectUniverse(num_timestamps=self.num_timestamps) 
        self.object_universe.add_camera(self.camera).\
                             add_viewable_objects(self.viewable_objects)
        
        self.cv.set_cv_ids_for_all_camera_time()

        # Rendering
        renderable_objects = [
                               self.boundary,
                               self.object_universe,
                             ] 

        RenderOrchestrator(self.num_timestamps, 
                           seconds_per_timestamp=0.2,
                           renderable_objects=renderable_objects).run()
        
        
    #     self.camera_renderer = CameraRenderer(self.camera)
    #     self.viewable_objects_renderer = ViewableObjectsRenderer(self.viewable_objects, computer_vision=self.cv)
    #     self.boundary_renderer = BoundaryRenderer(self.boundary)

    #     self.renderers = [
    #                         self.camera_renderer,
    #                         self.viewable_objects_renderer,
    #                         self.boundary_renderer
    #     ]

    #     self.animator = Animator(element_renderers=self.renderers, num_timestamps=self.num_timestamps, seconds_per_timestamp=0.2)
    #     TKRenderer().set_canvas_height(800).\
    #                  set_canvas_width(900).\
    #                  set_scale(1).\
    #                  set_mouse_click_callback(self.animator.play)

    # def run(self):
    #     TKRenderer().start_tk_event_loop()

if __name__ == '__main__':
    Demo()