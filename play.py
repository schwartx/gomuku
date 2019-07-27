import pickle

from game import Board, Game
from mcts_alphaZero import MCTSPlayer
from policy_value_net_numpy import PolicyValueNetNumpy
from human import Human

class Play:
    def __init__(self):
        policy_param = pickle.load(open('best_policy_8_8_5.model', 'rb'),
                                                            encoding='bytes')
        best_policy = PolicyValueNetNumpy(8, 8, policy_param)
        mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=400)
        human = Human()

        self.game = Game(Board(width=8, height=8, n_in_row=5), human, mcts_player)
        # self.turn = True

    def step(self, location=None):
        if location:
            location, end, winner = self.game.play()
        else:
            _, end, winner = self.game.play(location)

        return location, end, winner

if '__name__' == '__main__':
    p = Play()
    print(p)
    turn = True
    while True:
        turn = not turn
        if turn:
            location = input("Your move: ")
            _, end, winner = p.game.play(location)
            location = None
        else:
            location, end, winner = p.game.play()
            print("AI move:", location)
