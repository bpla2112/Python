from battleshipGame import BattleshipGame
from tkinter import *
from tkinter import ttk
import socket 
from socket import *
import threading
from socket import *
import sys

from PIL import Image, ImageTk

import udpchatserver
import os

# Globals
EntryBox = '' 
Chatbox = ''
scrollbar = ''
SendButton = ''

def parseIncoming():
	if game.gameStatus == 'WAITING FOR INPUT':
		startGame.leftGridFooter['text'] = 'Your Turn'
		startGame.rightGridFooter['text'] = ''
		updateGridImages(startGame.leftGridPositions, game.player.oceanSpace)
		return

	if game.gameStatus == 'WAITING FOR OPPONENT':
		startGame.rightGridFooter['text'] = "Opponent's Turn"
		startGame.leftGridFooter['text'] = ''

	if game.gameStatus == 'WON' or game.gameStatus == 'LOST':
		return

	msg = game.parseIncoming()

	if msg == 'OPPONENT READY':
		startGame.rightGridFooter['text'] = 'Opponent Ready'
		startGame.rightGridFooter['style'] = 'green/none.TLabel'

	if game.gameStatus == 'LOST':
		startGame.leftGridHeader['text'] = game.player.name + ' Lost'
		startGame.rightGridHeader['text'] = game.opponent.name + ' Won'

		startGame.leftGridHeader['style'] = 'red/none.TLabel'
		startGame.rightGridHeader['style'] = 'green/none.TLabel'

		startGame.leftGridFooter['text'] = ''
		startGame.rightGridFooter['text'] = ''

	root.after(100, parseIncoming)

def newGame(playerName):
	global rootContent

	rootContent.destroy()
	rootContent = ttk.Frame(root, padding=(30, 30, 30, 30))

	statusLabel = ttk.Label(rootContent, text='Waiting for player ...')
	rootContent.grid(column=0, row=0, sticky=(N, S, E, W))
	statusLabel.grid()

	root.update()

	game.setPlayerName(playerName)
	game.newGame()

	startGame()

def connectGame(ip, port):
	global rootContent

	rootContent.destroy()
	rootContent = ttk.Frame(root, padding=(30, 30, 30, 30))

	statusLabel = ttk.Label(rootContent, text='Connecting ...')

	rootContent.grid(column=0, row=0, sticky=(N, S, E, W))
	statusLabel.grid()

	root.update()

	game.joinGame(ip, port)

	startGame()

def connectMenu(playerName):
	global rootContent

	rootContent.destroy()
	rootContent = ttk.Frame(root, padding=(30, 30, 30, 30))

	ipLabel = ttk.Label(rootContent, text="IP", width=5)
	portLabel = ttk.Label(rootContent, text="Port", width=5)
	
	ipEntry = ttk.Entry(rootContent)
	portEntry = ttk.Entry(rootContent)

	connectButton = ttk.Button(rootContent, text='Connect', command= lambda: connectGame(ipEntry.get(), portEntry.get()), width=15)

	ipEntry.insert(END, 'localhost')
	portEntry.insert(END, game.getPort())

	rootContent.grid(column=0, row=0, sticky=(N, S, E, W))
	ipLabel.grid(column=0, row=0)
	portLabel.grid(column=0, row=1)
	ipEntry.grid(column=1, row=0)
	portEntry.grid(column=1, row=1)
	connectButton.grid(column=0, row=2, columnspan=2, sticky=(E, W), pady=5)

	ipEntry.focus()

	root.bind('<Return>', lambda x: connectGame(ipEntry.get(), portEntry.get()))

	game.setPlayerName(playerName)

def mainMenu():
	nameLabel = ttk.Label(rootContent, text="Name", width=5)
	nameEntry = ttk.Entry(rootContent)
	blankLabel = ttk.Label(rootContent)

	newGameButton = ttk.Button(rootContent, text='New Game', command= lambda: newGame(nameEntry.get()), width=15)
	connectGameButton = ttk.Button(rootContent, text='Connect To Player', command= lambda: connectMenu(nameEntry.get()), width=15)
	
	nameEntry.insert(END, 'Player')

	rootContent.grid(column=0, row=0, sticky=(N, S, E, W))
	nameLabel.grid(column=0, row=0)
	nameEntry.grid(column=1, row=0)
	blankLabel.grid(column=0, row=1)
	newGameButton.grid(column=0, row=2, columnspan=2, sticky=(E, W))
	connectGameButton.grid(column=0, row=3, columnspan=2, sticky=(E, W))

	nameEntry.focus()

def updateGridImages(_grid, oceanSpace):
	for row in range(0, game.oceanSize):
		for col in range(0, game.oceanSize):
			if oceanSpace.grid[row][col] == '~':
				_grid[row][col]['image'] = images['ocean']
			elif oceanSpace.grid[row][col] == '+':
				_grid[row][col]['image'] = images['ship']
			elif oceanSpace.grid[row][col] == '*':
				_grid[row][col]['image'] = images['unavail']
			elif oceanSpace.grid[row][col] == '-':
				_grid[row][col]['image'] = images['atk']
			elif oceanSpace.grid[row][col] == 'x':
				_grid[row][col]['image'] = images['shipatk']


	root.update()

def placeShip(grid, row, col):
	if game.gameStatus == 'PLACING SHIPS':
		if game.placeShip(row, col) == 'SHIPS PLACED':
			startGame.leftGridFooter.grid_forget()
			startGame.leftGridFooterButton.grid(column=0, row=2, pady=15)

	elif game.gameStatus == 'SHIPS PLACED':
		if game.placeShip(row, col) == 'PLACING SHIPS':
			startGame.leftGridFooter.grid(column=0, row=2, pady=20)
			startGame.leftGridFooterButton.grid_forget()

	updateGridImages(grid, game.player.oceanSpace)

def attackShip(grid, row, col):
	if game.gameStatus == 'WAITING FOR INPUT':
		if game.attackShip(row, col):
			updateGridImages(grid, game.opponent.oceanSpace)

			if game.gameStatus == 'WON':
				startGame.leftGridHeader['text'] = game.player.name + ' Won'
				startGame.rightGridHeader['text'] = game.opponent.name + ' Lost'

				startGame.leftGridHeader['style'] = 'green/none.TLabel'
				startGame.rightGridHeader['style'] = 'red/none.TLabel'

				startGame.leftGridFooter['text'] = ''
				startGame.rightGridFooter['text'] = ''

		root.after(100, parseIncoming)

def declareReady(grid):
	game.declareReady()
	startGame.leftGridFooter.grid(column=0, row=2, pady=20)
	startGame.leftGridFooterButton.grid_forget()
	startGame.leftGridFooter['style'] = 'green/none.TLabel'
	startGame.leftGridFooter['text'] = 'Ready'
	updateGridImages(grid, game.player.oceanSpace)

def startGame():
	global rootContent

	root.after(100, parseIncoming)

	rootContent.destroy()

	#root frames
	rootContent = ttk.Frame(root, padding=(5, 5, 5, 5))
	headerFrame = ttk.Frame(rootContent, borderwidth=5, relief="ridge", width=800, height=100)
	oceanFrame = ttk.Frame(rootContent, borderwidth=5, relief="ridge", width=800, height=550)
	chatFrame = ttk.Frame(rootContent, borderwidth=5, relief="ridge", width=200, height=650)

	rootContent.grid(column=0, row=0, sticky=(N, S, E, W))
	headerFrame.grid(column=0, row=0, sticky=(N, E, W), padx=5, pady=5)
	oceanFrame.grid(column=0, row=1, sticky=(N, S, E, W), padx=5, pady=5)
	chatFrame.grid(column=1, row=0, rowspan=2, sticky=(N, S, E), padx=5, pady=5)

	rootContent.columnconfigure(0, weight=1)
	rootContent.rowconfigure(0, weight=1)
	oceanFrame.columnconfigure(0, weight=1)
	oceanFrame.rowconfigure(0, weight=1)
	headerFrame.columnconfigure(0, weight=1)
	headerFrame.rowconfigure(0, weight=1)
	chatFrame.columnconfigure(0, weight=1)
	chatFrame.rowconfigure(0, weight=1)

	#header contents
	headerLabel = ttk.Label(headerFrame, text="Battleship", justify="center")
	headerLabel.configure(font=("Helvetica", 20, ""))
	headerLabel['style'] = 'red/none.TLabel'

	headerLabel.grid(column=0, row=0, pady=30)

	#ocean contents
	leftFrame = ttk.Frame(oceanFrame, borderwidth=5, relief="sunken", width=400, height=550)
	rightFrame = ttk.Frame(oceanFrame, borderwidth=5, relief="sunken", width=400, height=550)
	leftGridFrame = ttk.Frame(leftFrame, borderwidth=5, width=380, height=380)
	rightGridFrame = ttk.Frame(rightFrame, borderwidth=5, width=380, height=380)

	leftFrame.grid(column=0, row=0, sticky=(N, E, W))
	rightFrame.grid(column=1, row=0, sticky=(N, E, W))
	leftGridFrame.grid(column=0, row=1)
	rightGridFrame.grid(column=0, row=1)

	leftFrame.columnconfigure(0, weight=1)
	rightFrame.rowconfigure(0, weight=1)

	startGame.leftGridPositions = [ [] for _ in range(game.oceanSize) ]
	rightGridPositions = [ [] for _ in range(game.oceanSize) ]
	posSize = int(leftGridFrame['width'] / game.oceanSize)

	initImages(posSize)

	for _row in range(0, game.oceanSize):
		for _col in range(0, game.oceanSize):
			startGame.leftGridPositions[_row].append(ttk.Button(leftGridFrame, image=images['ocean']))
			rightGridPositions[_row].append(ttk.Button(rightGridFrame, image=images['ocean']))

			startGame.leftGridPositions[_row][_col]['command'] = lambda grid=startGame.leftGridPositions, row=_row, col=_col: placeShip(grid, row, col)
			rightGridPositions[_row][_col]['command'] = lambda grid=rightGridPositions, row=_row, col=_col: attackShip(grid, row, col)

			startGame.leftGridPositions[_row][_col].grid(column=_col, row=_row, sticky=(N, S, E, W), padx=2, pady=2)
			rightGridPositions[_row][_col].grid(column=_col, row=_row, sticky=(N, S, E, W), padx=2, pady=2)

	startGame.leftGridHeader = ttk.Label(leftFrame, text=game.player.name, justify="center")
	startGame.rightGridHeader = ttk.Label(rightFrame, text=game.opponent.name, justify="center")

	# startGame.leftGridHeader = ttk.Label(leftFrame, text="player1", justify="center")
	# startGame.rightGridHeader = ttk.Label(rightFrame, text="player2", justify="center")

	startGame.leftGridFooterButton = ttk.Button(leftFrame, text="Ready", command= lambda grid=startGame.leftGridPositions: declareReady(grid))
	startGame.leftGridFooter = ttk.Label(leftFrame, text="Click to place ships.", justify="center")
	startGame.rightGridFooter = ttk.Label(rightFrame, text="Waiting for opponent.", justify="center")

	startGame.leftGridHeader.grid(column=0, row=0, pady=20)
	startGame.rightGridHeader.grid(column=0, row=0, pady=20)

	startGame.leftGridFooter.grid(column=0, row=2, pady=20)
	startGame.rightGridFooter.grid(column=0, row=2, pady=20)
	showPlayerChat()
	root.update()
	root.minsize(root.winfo_width(), root.winfo_height())

def initImages(size):
	buf = Image.open('images/ocean.png').resize((size, size), Image.ANTIALIAS)
	images['ocean'] = ImageTk.PhotoImage(buf)

	buf = Image.open('images/ship.png').resize((size, size), Image.ANTIALIAS)
	images['ship'] = ImageTk.PhotoImage(buf)

	buf = Image.open('images/unavail.png').resize((size, size), Image.ANTIALIAS)
	images['unavail'] = ImageTk.PhotoImage(buf)

	buf = Image.open('images/shipatk.png').resize((size, size), Image.ANTIALIAS)
	images['shipatk'] = ImageTk.PhotoImage(buf)

	buf = Image.open('images/atk.png').resize((size, size), Image.ANTIALIAS)
	images['atk'] = ImageTk.PhotoImage(buf)

# Player Chat
# ---------------------------------------------------------

# Create the actual chat window
def showPlayerChat():
	global EntryBox, Chatbox, scrollbar, SendButton
	playerChat = Toplevel()
	playerChat.geometry('%dx%d+%d+%d' % (800, 600, 0, 0))

	# Scrollbar
	scrollbar = Scrollbar(playerChat)

	# Chatbox
	Chatbox = Text(playerChat, bd=0, bg="white", height="8", width="50", font="Arial", yscrollcommand=scrollbar.set)
	Chatbox.insert(END, "{} connecting to chat...\n".format(game.player.name))
	clientSocket.sendall(bytearray(game.player.name, 'UTF-8'))
	Chatbox.config(state=DISABLED)

	# Button
	SendButton = Button(playerChat, font=30, text="Send", width=12, height=5,bd=0, bg="#2ecc71", activebackground="#FFBF00")
	SendButton.bind("<Button-1>", handleClick)
	# Input Field
	EntryBox = Text(playerChat, bd=0, bg="white",width="29", height="5", font="Arial")
	EntryBox.bind("<Return>", DisableEntry)
	EntryBox.bind("<KeyRelease-Return>", handleEnter)

	# Widget Placement
	scrollbar.place(x=776,y=6, height=486)
	Chatbox.place(x=6,y=6, height=486, width=770)
	EntryBox.place(x=128, y=495, height=115, width=650)
	SendButton.place(x=6, y=495, height=115)

def receive():
    global EntryBox, Chatbox, scrollbar, SendButton
    while True:
        try:
            sender = clientSocket.recv(1024).decode()
            data = clientSocket.recv(1024).decode().strip('\n')
        except:
            LoadConnectionInfo(Chatbox, '\n [ Your partner has disconnected ] \n')
            break
        if data != '':
            LoadOtherEntry(Chatbox, data, str(game.player.name))
        else:
            LoadConnectionInfo(Chatbox, '\n [ Your partner has disconnected ] \n')
            break

# Events

# Mouse Event
def handleClick(event):
    global EntryBox, Chatbox, scrollbar, SendButton
    message = FilteredMessage(EntryBox.get("0.0",END))
    LoadMyEntry(Chatbox, message)
    Chatbox.yview(END)
    EntryBox.delete("0.0",END)
    clientSocket.sendall(bytearray(message, 'UTF-8'))

# Keyboard Events
def handleEnter(event):
    global EntryBox, Chatbox, scrollbar, SendButton
    EntryBox.config(state=NORMAL)
    handleClick(event)

def DisableEntry(event):
    global EntryBox, Chatbox, scrollbar, SendButton
    EntryBox.config(state=DISABLED)

# Message Functions    
def FilteredMessage(message):
    EndFiltered = ''
    for i in range(len(message)-1,-1,-1):
        if message[i]!='\n':
            EndFiltered = message[0:i+1]
            break
    for i in range(0,len(EndFiltered), 1):
            if EndFiltered[i] != "\n":
                    return EndFiltered[i:]+'\n'
    return ''
    
def LoadConnectionInfo(Chatbox, message):
    if message != '':
        Chatbox.config(state=NORMAL)
        if Chatbox.index('end') != None:
            Chatbox.insert(END, message+'\n')
            Chatbox.config(state=DISABLED)
            Chatbox.yview(END)

def LoadMyEntry(Chatbox, message):
    if message != '':
        Chatbox.config(state=NORMAL)
        if Chatbox.index('end') != None:
            LineNumber = float(Chatbox.index('end'))-1.0
            Chatbox.insert(END, "You: " + str(message))
            Chatbox.tag_add("You", LineNumber, LineNumber+0.4)
            Chatbox.tag_config("You", foreground="#FF8000", font=("Arial", 12, "bold"))
            Chatbox.config(state=DISABLED)
            Chatbox.yview(END)


def LoadOtherEntry(Chatbox, message, name):
    if message != '':
        Chatbox.config(state=NORMAL)
        if Chatbox.index('end') != None:
            try:
                LineNumber = float(Chatbox.index('end'))-1.0
            except:
                pass
            Chatbox.insert(END, name + ": " + str(message) + "\n")
            Chatbox.tag_add(name, LineNumber, LineNumber+0.6)
            Chatbox.tag_config(name, foreground="#04B404", font=("Arial", 12, "bold"))
            Chatbox.config(state=DISABLED)
            Chatbox.yview(END)
# ---------------------------------------------------------
# Player Chat End

game = BattleshipGame()

try:
	#launch server
	chatsrv = udpchatserver.main()
except OSError:
	pass

root = Tk()
root.title('Battleship')

ttk.Style().configure('green/none.TLabel', foreground='green')
ttk.Style().configure('red/none.TLabel', foreground='red')

rootContent = ttk.Frame(root, padding=(30, 30, 30, 30))

images = {}

clientSocket = socket(AF_INET, SOCK_STREAM)
HOST = 'localhost'
PORT = 5023
clientSocket.connect((HOST, PORT))     
print('Connected to remote host...')

thread_receive = threading.Thread(target = receive)
thread_receive.start()

mainMenu()
uname = game.player.name

root.mainloop()