from copy import deepcopy
import random
from turtle import forward
from C4.utils import C4_apply_move, C4_encode_state, C4_format_state, C4_get_available_moves, C4_is_terminal
from TTT.utils import TTT_encode_state, TTT_get_available_moves, TTT_apply_move, TTT_format_state, TTT_is_terminal
import json, os, pandas as pd, torch
import torch.nn as nn
import torch.optim as optim

class RL_Algos:
	def __init__(self, get_moves, apply_move, is_terminal, encode_state, copy_state_func=None):
		self.get_moves = get_moves
		self.apply_move = apply_move
		self.is_terminal = is_terminal
		self.copy_state = copy_state_func if copy_state_func is not None else (lambda s: s.copy())
		self.encode_state = encode_state

class JSonUtils:
	def get_json_path(game: str):
		return f"Data/{game}.json"

	def load(game: str):
		path_ = JSonUtils.get_json_path(game)
		if not os.path.exists(path_):
			return None

		with open(path_, 'r') as f:
			return json.load(f)

	def save(game: str, config: dict):
		with open(JSonUtils.get_json_path(game), 'w') as f:
			json.dump(config, f)

	########## Tabular RL stuff ##########

	def get_epsilon(game: str) -> float:
		return JSonUtils.load(game)["epsilon"]

	def update_epsilon(game: str, val: float):
		j = JSonUtils.load(game)
		j['epsilon'] = val
		JSonUtils.save(game, j)

	def get_qtable(game: str):
		path_ = JSonUtils.load(game)['qtable']
		if not os.path.exists(path_):
			return None

		df = pd.read_csv(path_, index_col=0)
		df.columns = df.columns.astype(int)
		return df

	def set_qtable(game: str, table: pd.DataFrame):
		path_ = JSonUtils.load(game)['qtable']
		table.to_csv(path_)

class Tabular_QRL:
	TTT = RL_Algos(
		get_moves=TTT_get_available_moves, 
		apply_move=TTT_apply_move, 
		is_terminal=TTT_is_terminal,
		encode_state=TTT_encode_state
	)
	C4 = RL_Algos(
		get_moves=C4_get_available_moves,
		apply_move=C4_apply_move,
		is_terminal=C4_is_terminal,
		encode_state=C4_encode_state,
		copy_state_func=lambda s: deepcopy(s)
	)

	game_dict = {
		"TTT": TTT,
		"C4": C4
	}

	# passive, policy-evaluating RL
	discount = 0.9
	learning_rate = 0.3		# Qval(state, action) + learning_rate * TD Error (=difference between Qval observed - Qval expected)
	exploration_discount = 0.9999

	run_avg_tderr = []

	def evaluate(game, state, team, utility_func):
		def get_or_create_state_entry(qtable: pd.DataFrame, state: str, max_n_moves):
			if state not in qtable.index:
				qtable.loc[state] = [0.0] * max_n_moves
		
			return qtable.loc[state_encoded]

		game_funcs = Tabular_QRL.game_dict.get(game, None)
		if game_funcs is None:
			return -1

		#region json
		j_ = JSonUtils.load(game)

		# add entry if none exists
		if j_ is None:
			JSonUtils.save(game, {
				'epsilon': 1,
				'qtable': f'Data/{game}_TQRL.csv'
			})

			j_ = JSonUtils.load(game)

			if j_ is None:
				return -1
		#endregion

		qtable = JSonUtils.get_qtable(game)
		max_n_moves = 7 if game == 'C4' else 9
		if qtable is None:
			qtable = pd.DataFrame(columns=['state'] + list(range(max_n_moves))).set_index("state")

		epsilon = JSonUtils.get_epsilon(game)
		state_encoded = game_funcs.encode_state(state)
		state_qvals = get_or_create_state_entry(qtable, state_encoded, max_n_moves)

		if game_funcs.is_terminal(state):
			return -1

		# action selection: random if random threshold > 1-e, else policy.
		prob = float(random.randint(0, 100)) / 100
		moves = game_funcs.get_moves(state)
		action = None
		learning = False

		# exploration - random move
		if prob > (1 - epsilon):
			# choose random action
			action = random.choice(moves)
			learning = True
		# policy enforcement
		else:
			max_qval = -10000
			for move in moves:
				if state_qvals[move] > max_qval:
					max_qval = state_qvals[move]
					action = move
					

		# learning timestep:
		if learning:
			new_state = game_funcs.apply_move(game_funcs.copy_state(state), action, team)
			expected_qval = state_qvals[action]

			new_state_encoded = game_funcs.encode_state(new_state)
			new_state_qvals = get_or_create_state_entry(qtable, new_state_encoded, max_n_moves)

			max_qval2 = -10000
			for move in game_funcs.get_moves(new_state):
				if new_state_qvals[move] > max_qval2:
					max_qval2 = new_state_qvals[move]

			observed_qval = utility_func(new_state, game_funcs.is_terminal(new_state)) + Tabular_QRL.discount * max_qval2
			td_error = observed_qval - expected_qval

			# stats stuff
			Tabular_QRL.run_avg_tderr.append(td_error)
			# discount epsilon by the state discount value too
			JSonUtils.update_epsilon(game, epsilon * Tabular_QRL.exploration_discount)

			qtable.loc[state_encoded, action] = expected_qval + Tabular_QRL.learning_rate * td_error
			JSonUtils.set_qtable(game, qtable)

		# behaviour timestep: select action by Qval and don't update Qval. -> exploration factor epsilon embedded in table somewhere to check whether it needs to be done?
		return action

	def get_avg_tderr():
		avg = sum(Tabular_QRL.run_avg_tderr) / len(Tabular_QRL.run_avg_tderr)
		Tabular_QRL.run_avg_tderr.clear()
		return avg

class DQ_Network(nn.Module):
	def __init__(self, state_size: int, n_actions: int):
		super().__init__()

		self.network_width = 128
		self.net = nn.Sequential(
			nn.Linear(state_size, self.network_width),
			nn.ReLU(),
			nn.Linear(self.network_width, self.network_width),
			nn.ReLU(),
			nn.Linear(self.network_width, n_actions)
		)

	# takes in an encoded version of the state and returns a network of n q-vals for every available move.
	def forward(self, x: torch.Tensor) -> torch.Tensor:
		return self.net(x)

	def save(self, path):
		torch.save(self.state_dict(), path)

class DQN_RL:
	TTT = RL_Algos(
		get_moves=TTT_get_available_moves, 
		apply_move=TTT_apply_move, 
		is_terminal=TTT_is_terminal,
		encode_state=TTT_encode_state
	)
	C4 = RL_Algos(
		get_moves=C4_get_available_moves,
		apply_move=C4_apply_move,
		is_terminal=C4_is_terminal,
		encode_state=C4_encode_state,
		copy_state_func=lambda s: deepcopy(s)
	)

	game_dict = {
		"TTT": TTT,
		"C4": C4
	}

	# state size considering encoding 
	# -> vector [team, empty, opponent] for every tile = 3*n_tiles in state 
	# 3*9=27 (TTT), 3*6*7=3*42 = 126 (C4)
	state_sizes = {
		"TTT": 27,
		"C4": 126
	}
	n_actions = {
		"TTT": 9,
		"C4": 7
	}

	# passive, policy-evaluating RL
	discount = 0.9
	learning_rate = 0.3		# Qval(state, action) + learning_rate * TD Error (=difference between Qval observed - Qval expected)
	exploration_discount = 0.9999

	run_avg_tderr = []

	def get_epsilon(game: str):
		return JSonUtils.get_epsilon(game)

	def to_tensor(base_encoding: str) -> torch.Tensor:
		output: list[int] = []
		n_since_break = 0

		for char in base_encoding:
			# space used to signal column end in c4 encoding -> fill up to 6
			if char == ' ':
				output += [0, 1, 0] * int(6 - n_since_break)
				n_since_break = 0
				continue
			if char == 'e':
				output += [0, 1, 0]
				n_since_break += 1
				continue
			if char == 'x':
				output += [1, 0, 0]
				n_since_break += 1
				continue
			if char == 'o':
				output += [0, 0, 1]
				n_since_break += 1
				continue

		#print(f"Encoded state {base_encoding} to {len(output)} tokens.")
		return torch.tensor(output, dtype=torch.float32)

	def evaluate(game, state, team, utility_func):
		game_funcs = DQN_RL.game_dict.get(game, None)
		j_ = JSonUtils.load(game)

		if j_ is None:
			JSonUtils.save(game, {
				'epsilon': 1,
				'qtable': f'Data/{game}_TQRL.csv'
			})

			j_ = JSonUtils.load(game)

			if j_ is None:
				return -1

		if game_funcs is None:
			return -1

		def get_or_create_model(game: str, state_size: int, n_actions: int) -> DQ_Network:
			model = DQ_Network(state_size=state_size, n_actions=n_actions)
			try:
				model.load_state_dict(torch.load(f"Data/{game}_DQN.pth"))
			except FileNotFoundError:
				print(f"Couldn't find an existing model for game {game}")

			# untrained model if none
			return model

		model = get_or_create_model(game=game, state_size=DQN_RL.state_sizes[game], n_actions=DQN_RL.n_actions[game])
		epsilon = JSonUtils.get_epsilon(game)

		base_encoding = game_funcs.encode_state(state)
		tensor_encoding = DQN_RL.to_tensor(base_encoding)
		moves = game_funcs.get_moves(state)

		if random.random() > (1 - epsilon):
			action = random.choice(moves)
			learning = True	
		else:
			with torch.no_grad():
				# get qvals through DQN
				q_vals = model(tensor_encoding).numpy()
			action = max(moves, key=lambda m: q_vals[m])
			learning = False

		if learning:
			new_state = game_funcs.apply_move(game_funcs.copy_state(state), action, team)
			terminal = game_funcs.is_terminal(new_state)
			reward = utility_func(new_state, terminal)
			new_tensor_encoding = DQN_RL.to_tensor(game_funcs.encode_state(new_state))

			# get existing/expected q_vals
			q_vals = model(tensor_encoding)
			with torch.no_grad():
				next_qval = model(new_tensor_encoding).max().item()
				target = reward if terminal else reward + DQN_RL.discount * next_qval

			target_qval = q_vals.clone().detach()
			target_qval[action] = target

			loss = nn.MSELoss()(q_vals, target_qval)
			DQN_RL.run_avg_tderr.append(loss.item())
			optimiser = optim.Adam(model.parameters(), lr=DQN_RL.learning_rate)
			optimiser.zero_grad()
			loss.backward()
			optimiser.step()

			JSonUtils.update_epsilon(game, epsilon * DQN_RL.exploration_discount)
			model.save(f"Data/{game}_DQN.pth")

		return action

	def get_avg_tderr():
		avg = sum(DQN_RL.run_avg_tderr) / len(DQN_RL.run_avg_tderr)
		DQN_RL.run_avg_tderr.clear()
		return avg
