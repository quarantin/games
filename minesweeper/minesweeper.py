#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import random

SIZE  = 20
MARGIN = 5

BLACK = (000, 000, 000)
GREY  = (186, 189, 182)
GREEN = (000, 255, 000)
FLAG  = (000, 000, 255)
RED   = (255, 000, 000)
WHITE = (255, 255, 255)

BOMBS = [
	(222, 222, 220),
	(221, 250, 195),
	(236, 237, 191),
	(237, 218, 180),
	(237, 195, 138),
	(255, 000, 000),
	(254, 167, 133),
	(255, 000, 000),
	(255, 000, 000),
]

class Cell:

	def __init__(self, row, col):
		self.row = row
		self.col = col
		self.bomb = False
		self.bombs = 0
		self.flagged = False
		self.visible = False

class MineSweeper:

	def __init__(self, rows=30, columns=30, bombs=100):

		self.grid = []
		self.rows = rows
		self.columns = columns
		self.bombs = []
		self.flags = []

		for row in range(rows):
			self.grid.append([])
			for col in range(columns):
				self.grid[row].append(Cell(row, col))

		while bombs > 0:
			row = random.randint(0, rows    - 1)
			col = random.randint(0, columns - 1)
			cell = self.grid[row][col]
			if cell.bomb != True:
				cell.bomb = True
				cell.bombs = 0
				if cell not in self.bombs:
					self.bombs.append(cell)
				self.increment_bombs(row, col)
				bombs = bombs - 1

	def check_win(self):

		for cell in self.bombs:
			if not cell.flagged:
				return

		for cell in self.flags:
			if not cell.bomb:
				return

		self.won = True
		print('Success!')

	def flag_cell(self, cell):
		cell.flagged = not cell.flagged
		if cell.flagged and cell not in self.flags:
			self.flags.append(cell)
		elif not cell.flagged and cell in self.flags:
			self.flags.remove(cell)

	def increment_bombs(self, row, col):
		for x in range(col - 1, col + 2):
			for y in range(row - 1, row + 2):
				if x >= 0 and y >= 0 and x < self.rows and y < self.columns and (x != col or y != row):
					cell = self.grid[y][x]
					if not cell.bomb:
						cell.bombs = cell.bombs + 1

	def visit_cells(self, row, col):

		visited = {}
		cells = [ self.grid[row][col] ]

		while len(cells) > 0:
			cell = cells.pop()
			cell.visible = True
			visited[cell] = True
			for x in range(cell.col - 1, cell.col + 2):
				for y in range(cell.row - 1, cell.row + 2):
					if x >= 0 and y >= 0 and x < self.rows and y < self.columns and (x != col or y != row):
						other_cell = self.grid[y][x]
						if other_cell not in visited:
							if not other_cell.bomb:
								other_cell.visible = True
								if other_cell.bombs == 0:
									cells.append(other_cell)

	def process_pygame_events(self):

		for event in pygame.event.get():

			if event.type == pygame.QUIT:
				self.running = False

			elif self.lost or self.won:
				continue

			elif event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				col = pos[0] // (SIZE + MARGIN)
				row = pos[1] // (SIZE + MARGIN)
				cell = self.grid[row][col]
				if event.button == 3 and not cell.visible:
					self.flag_cell(cell)

				elif cell.bomb and not cell.flagged:
					print('A bomb has exploded!')
					self.lost = True

				else:
					self.visit_cells(row, col)

	def run(self):

		self.won = False
		self.lost = False
		self.running = True
		size = SIZE + MARGIN

		WINDOW_SIZE = [self.columns * (SIZE + MARGIN), self.rows * (SIZE + MARGIN)]

		pygame.init()
		screen = pygame.display.set_mode(WINDOW_SIZE)
		pygame.display.set_caption('Mine Sweeper')
		font = pygame.font.SysFont('didot.ttc', 30)
		clock = pygame.time.Clock()

		while self.running:

			self.process_pygame_events()

			screen.fill(WHITE)
		 
			for row in self.grid:
				for cell in row:

					label = ''
					color = GREY

					if cell.visible:
						color = BOMBS[cell.bombs]
						if cell.bombs > 0:
							label = str(cell.bombs)

					if cell.flagged:
						color = FLAG

					if self.lost and cell.bomb:
						color = RED

					if self.won and cell.bomb:
						color = GREEN

					rect = pygame.Rect(cell.col * size, cell.row * size, SIZE, SIZE)
					pygame.draw.rect(screen, color, rect)

					if label:
						img = font.render(label, True, BLACK)
						screen.blit(img, (cell.col * size + SIZE / 4, cell.row * size + SIZE / 8))
		 
			clock.tick(60)
		 
			pygame.display.flip()

			self.check_win()

if __name__ == '__main__':
	MineSweeper(rows=30, columns=30, bombs=100).run()
