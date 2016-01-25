#!/opt/local/bin/python


class Hanabi_Card(object):
    def __init__(self, number, color):
        """Return a hanabi_card object whose number is *number* and color is *color*""" 
        self.number = int(number)
        self.color = color
        
    def get_number(self):
        return self.number
        
    def get_color(self):
        return self.color