#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import random

from collections import deque
from functools import total_ordering

@total_ordering
class Combination:

	NENETTE = [ 2, 2, 1 ]

	def __init__(self):
		self.draw = [ 0, 0, 0 ]

	def init():
		with open('421.json') as fd:
			Combination.combinations = json.loads(fd.read())['combinations']

	def __str__(self):
		return str(self.draw)

	def as_string(self):
		return ''.join([ str(x) for x in self.draw ])

	def __eq__(self, other):
		return self.draw == other.draw

	def __lt__(self, other):

		if other.draw == Combination.NENETTE:
			return False

		for combination in Combination.combinations:

			if self.draw == combination['draw']:
				return False

			if other.draw == combination['draw']:
				return True

		for d1, d2 in zip(self.draw, other.draw):

			if d1 < d2:
				return True

			if d1 > d2:
				return False

		return False

	def get_tokens(self):

		for combination in Combination.combinations:
			if self.draw == combination['draw']:
				return combination['tokens']

		return 1

	def is_fiche(self):
		return self.draw.count(1) == 2

	def is_suite(self):
		d = self.draw
		return d[0] + 1 == d[1] and d[1] + 1 == d[2]

	def roll_dice(self):
		return random.randint(1, 6)

	def roll(self, first=True, second=True, third=True):

		if first:
			self.draw[0] = self.roll_dice()

		if second:
			self.draw[1] = self.roll_dice()

		if third:
			self.draw[2] = self.roll_dice()

		self.draw.sort()
		if not self.is_fiche() and not self.is_suite():
			self.draw.reverse()
	
class Player:

	pad = 0

	def __init__(self, name):
		self.name = name
		self.tokens = 0
		self.combination = Combination()
		if len(name) > Player.pad:
			Player.pad = len(name)

	def __str__(self):
		name = self.name + '\'s'
		return '%s tokens: %s roll: %s -> %s' % (name.rjust(Player.pad + 2), str(self.tokens).rjust(2), self.combination, self.combination.get_tokens())

	def roll(self, first=True, second=True, third=True, rolls=3):

		rolls = rolls - 1

		self.combination.roll(first=first, second=second, third=third)
		print('\t %s' % self.combination)

		if rolls == 0:
			print('')
			return 3 - rolls

		while True:

			try:
				response = input('> ')

				if response.strip() == '':
					print('')
					return 3 - rolls

				reroll = [ int(i) for i in response.split(' ') ]
				first  = 1 in reroll
				second = 2 in reroll
				third  = 3 in reroll
				return self.roll(first=first, second=second, third=third, rolls=rolls)

			except EOFError:
				sys.exit()

			except ValueError:
				pass

class FourTwentyOne:

	def __init__(self, names):
		self.pot = 21
		self.players = deque()
		for name in names:
			self.players.append(Player(name))
		Combination.init()
		random.seed(os.urandom(4))
		self.start()

	def debug(self, players):
		for player in players:
			print(player)
		print('')

	def get_losing_player_index(self):

		losing_index = -1
		losing_player = None

		for index, player in enumerate(self.players):
			if not losing_player or player.combination < losing_player.combination:
				losing_index = index
				losing_player = player

		return -losing_index

	def rotate(self):
		self.players.rotate(self.get_losing_player_index())

	def do_turn(self, players=None):

		if not players:
			players = deque(self.players)

		draw = {}
		first = True
		max_rolls = 3
		for player in players:
			print('=== ' + player.name + "\'s turn ===")
			rolls = player.roll(rolls=max_rolls)
			if first:
				first = False
				max_rolls = rolls

			combination = player.combination.as_string()
			if combination not in draw:
				draw[combination] = []

			draw[combination].append(player)

		players = sorted(players, key=lambda player: player.combination, reverse=True)

		result = deque()
		for player in players:
			combination = player.combination.as_string()
			if combination not in draw:
				continue
			ex_aequo = draw[combination]
			if len(ex_aequo) == 1:
				result.extend(ex_aequo)
			else:
				print('Players %s are ex aequo, need to replay' % (', '.join([ p.name for p in ex_aequo ])))
				ex_aequo = self.do_turn(ex_aequo)
				ex_aequo = sorted(ex_aequo, key=lambda player: player.combination, reverse=True)
				result.extend(ex_aequo)

		return result

	def charge_phase(self):

		self.turn = 1

		print('# Charge Phase\n')

		while self.pot > 0:

			print('# Turn %d\n' % self.turn)
			self.turn = self.turn + 1

			players = self.do_turn()
			tokens = min(self.pot, players[0].combination.get_tokens())
			self.pot = self.pot - tokens
			players[-1].tokens = players[-1].tokens + tokens

			self.debug(players)
			self.rotate()

		print('')
		for player in self.players:
			print('%s: %d tokens' % (player.name, player.tokens))

		print('')

	def discharge_phase(self):

		self.turn = 1

		print('# Discharge Phase\n')

		done = []
		while len(self.players) > 1:

			print('# Turn %d\n' % self.turn)
			self.turn = self.turn + 1

			players = self.do_turn()
			tokens = min(players[0].tokens, players[0].combination.get_tokens())
			players[0].tokens = players[0].tokens - tokens
			players[-1].tokens = players[-1].tokens + tokens

			self.debug(players)

			if players[0].tokens == 0:
				player = players.popleft()
				self.players.remove(player)
				done.append(player)
				print('>>> %s finished <<<\n' % player.name)

			self.rotate()

		player = players.popleft()
		self.players.remove(player)
		done.append(player)

		print('Game finished')
		for index, player in enumerate(done):
			print('%d: %s' % (index + 1, player.name))

	def start(self):
		self.charge_phase()
		self.discharge_phase()

def main():

	if len(sys.argv) < 2:
		print('Usage: %s players...' % sys.argv[0])
		sys.exit()

	FourTwentyOne(sys.argv[1:])

if __name__ == '__main__':
	main()
