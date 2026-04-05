from game import Game
from Algorithms.rl import DQN_RL

# init at 1 because only ever called after an episode.
n_episodes = 1
max_episodes = 50
update_interval = 50
train_ttt = False
game = None

win_dict = {
    'p1': 0,
    'draw': 0,
    'p2': 0
}

def select_correct_game():
    global correct_game

    if train_ttt and game.active_game == game.c4:
        game.close_c4()
        game.open_TTT()

    elif not train_ttt and game.active_game == game.ttt:
        game.close_TTT()
        game.open_c4()

    game.beforeUpdate.remove_listener(select_correct_game)


def on_game_end(winner):
    # access global variable
    global n_episodes
    global win_dict


    if "Player 1" in winner:
        win_dict['p1'] += 1
    elif winner == 'Draw':
        win_dict['draw'] += 1
    elif "Player 2" in winner:
        win_dict['p2'] += 1
    else:
        print(winner)

    if n_episodes % update_interval == 0:
        #print(f"Game {n_episodes} | epsilon: {DQN_RL.get_epsilon('TTT' if train_ttt else 'C4'):.4f} | avg TD err: {DQN_RL.get_avg_tderr():.4f}")
        total_games = win_dict['p1'] + win_dict['draw'] + win_dict['p2']
        print(f"Training ovr statistics (W / win%) in {total_games} matches:\n"\
            f"Player 1: {win_dict['p1']}/{total_games} - {(float(win_dict['p1']) / total_games):.2f}\n" \
            f"Draws: {win_dict['draw']}/{total_games} - {(float(win_dict['draw']) / total_games):.2f}\n" \
            f"Player 2: {win_dict['p2']}/{total_games} - {(float(win_dict['p2']) / total_games):.2f}\n"
        )
    
    # immediately restart a game until max episodes.
    if n_episodes <= max_episodes:
        n_episodes += 1
        if train_ttt:
            game.ttt.start()
        else:
            game.c4.start()
    else:
        print(n_episodes)
        game.request_close()

if __name__ == "__main__":
    game = Game("DQN Trainer", (1280, 720))
    game.beforeUpdate.add_listener(select_correct_game)

    options = ["Human", "Baseline", "MinMax", "MinMax-AB", "Tabular QRL", "DQN-RL"]

    train_ttt = False
    type1 = options[3]
    type2 = options[3]

    print(f"{type1} vs {type2} ({'TTT' if train_ttt else 'C4'})")

    # set DQN to train against the baseline:
    # assess training @ end of each run then restart game
    if train_ttt:
        game.ttt.set_player(1, type1)
        game.ttt.set_player(2, type2)
        game.ttt.on_game_end.add_listener(on_game_end)
    else:
        game.c4.set_player(1, type1)
        game.c4.set_player(2, type2)
        game.c4.on_game_end.add_listener(on_game_end)

    if train_ttt:
        game.ttt.start()
    else:
        game.c4.start()
    game.run()