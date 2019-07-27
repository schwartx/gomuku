class Human:
    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board, location=None):
        location = list(location)
        move = board.location_to_move(location)
        return move, location

    def __str__(self):
        return "Human {}".format(self.player)
