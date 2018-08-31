from tk_canvas_renderers.tk_renderer import TKRenderer

class Animator:
    def __init__(self, element_renderers=[], num_timestamps=0):
        self.element_renderers = element_renderers
        self.tk_renderer = TKRenderer()
        self.current_timestamp = 0
        self.num_timestamps = num_timestamps

    def play(self):
        for timestamp in range(self.current_timestamp, self.num_timestamps):
            for er in self.element_renderers:
                er.render(timestamp=timestamp)
                


        

