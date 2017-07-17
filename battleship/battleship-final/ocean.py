class Ocean:

	def __init__(self, size): #establish the grid
		self.size = size
		self.grid = [ ['~' for _ in range(size)] for _ in range(size) ]

	def updateGrid(self, value, coordinates):
		for coordinate in coordinates:
			x, y = coordinate	

			if (x > (self.size-1)) or (y > (self.size-1)):
				raise ValueError('coordinate out of scope', repr(coordinate))

		if value == '+':	

			for coordinate in coordinates:
				x, y = coordinate

				if self.grid[x][y] == '~':
					self.markGrid(value, coordinate)

					self.markGrid('*', (x-1, y))
					self.markGrid('*', (x, y-1))
					self.markGrid('*', (x, y+1))
					self.markGrid('*', (x+1, y))

				else:
					raise ValueError('position not available')

			return True

		if value == 'x':	#used location
			for coordinate in coordinates:
				x, y = coordinate

				if self.grid[x][y] == '+':
					self.markGrid(value, coordinate)

					self.markGrid('*', (x-1, y))
					self.markGrid('*', (x, y-1))
					self.markGrid('*', (x, y+1))
					self.markGrid('*', (x+1, y))

				elif self.grid[x][y] == '~':
					self.markGrid('-', coordinate)

				else:
					raise ValueError('position already attacked')

		if value == '~':	#RIP SHIP
			for coordinate in coordinates:
				x, y = coordinate

				if self.grid[x][y] == '+':
					self.markGrid(value, coordinate)

					self.markGrid('~', (x-1, y))
					self.markGrid('~', (x, y-1))
					self.markGrid('~', (x, y+1))
					self.markGrid('~', (x+1, y))

					for x in range(0, self.size):
						for y in range(0, self.size):
							if self.grid[x][y] == '+':
								self.markGrid('*', (x-1, y))
								self.markGrid('*', (x, y-1))
								self.markGrid('*', (x, y+1))
								self.markGrid('*', (x+1, y))

				else:
					raise ValueError('position not available')

	def markGrid(self, value, position): #making marks on the grid. 
		x, y = position

		if x > (self.size-1) or (y > self.size-1) or (x < 0) or (y < 0):
			return False

		if value == '~':
			if self.grid[x][y] == '+' or self.grid[x][y] == '*':
				self.grid[x][y] = '~'

		if value == '+':
			if self.grid[x][y] == '~':
				self.grid[x][y] = '+'

		if value == 'x':
			if self.grid[x][y] == '+' or self.grid[x][y] == '~' or self.grid[x][y] == '*':
				self.grid[x][y] = 'x'

		if value == '-':
			if self.grid[x][y] == '+' or self.grid[x][y] == '~' or self.grid[x][y] == '*':
				self.grid[x][y] = '-'

		if value == '*':
			if self.grid[x][y] == '~':
				self.grid[x][y] = '*'

		return True

	def cleanGrid(self, new = False): #clear everything
		for x in range(0, self.size):
			for y in range(0, self.size):
				if new == True:
					self.grid[x][y] = '~'

				else:
					if self.grid[x][y] == '*':
						self.grid[x][y] = '~'

	def spitOcean(self):
		for row in self.grid:
			for ele in row:
				print(ele + '   ',)

			print('\n')