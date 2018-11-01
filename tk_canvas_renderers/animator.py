from tk_canvas_renderers.tk_renderer import TKRenderer
import time

class Animator:
    def __init__(self, element_renderers=[], num_timestamps=0, seconds_per_timestamp=1):
        self.element_renderers = element_renderers
        self.tk_renderer = TKRenderer()
        self.current_timestamp = 0
        self.num_timestamps = num_timestamps
        self.seconds_per_timestamp = seconds_per_timestamp
        self.render_stationary_sub_elements()

    def set_element_renderers(self, element_renderers):
        self.element_renderers = element_renderers
        self.render_stationary_sub_elements()
        return self

    def get_element_renderers(self):
        return self.element_renderers

    def add_element_renderers(self, element_renderers):
        if type(element_renderers) != list:
            element_renderers = [element_renderers]
        self.element_renderers += element_renderers
        self.render_stationary_sub_elements()
        return self

    def render_stationary_sub_elements(self):
        for element in self.element_renderers:
            element.render()

        self.tk_renderer.update()

    def set_seconds_per_timestamp(self, seconds):
        self.seconds_per_timestamp = seconds
        return self

    def get_seconds_per_timestamp(self):
        return self.seconds_per_timestamp

    def play(self, *pargs, **kargs):
        for timestamp in range(self.current_timestamp, self.num_timestamps):
            for element in self.element_renderers:
                element.render(timestamp=timestamp)
                self.tk_renderer.update()
                time.sleep(self.seconds_per_timestamp)






