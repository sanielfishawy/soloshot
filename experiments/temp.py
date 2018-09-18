class foo:
    def __init__(self):
        self.h = {}
        self.key = "foo"

    def get_h(self):
        if self.key not in self.h:
            self.h[self.key] = 0
        return self.h[self.key]
    
    def set_h(self, value):
        self.get_h() = value
        return self.h


f = foo()

f.set_h(5)