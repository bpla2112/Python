class Player:

	def __init__(self, name, oceanSpace, noOfShips=5):
		self.name = name
		self.oceanSpace = oceanSpace
		self.gameScore = 0
		self.noOfShips = noOfShips
		self.shipsDestroyed = 0
		self.shipPositions = []
		self.ready = False
		self.port = -1

	def __str__(self):
		return self.name + " " + str(self.gameScore) + " " + str(self.noOfShips) + " " + str(self.shipsDestroyed) + " " + str(self.shipPositions) + " " + str(self.ready) + " " + str(self.port)

	def setName(self, name):
		self.name = name