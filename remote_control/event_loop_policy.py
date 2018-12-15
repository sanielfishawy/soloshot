import asyncio

class EventLoopPolicy(asyncio.DefaultEventLoopPolicy):

    def get_event_loop(self):
        """
        Get threads eventloope or create a new one
        """
        try:
            loop = super().get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        return loop