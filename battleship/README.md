<h1>
**multiplayer_battleship**
</h1>

<p>
**Video Here:** [https://youtu.be/e0pdN1UJ0tI](https://youtu.be/e0pdN1UJ0tI "Project Video")
</p>

- This game is designed to support up to 4 players. 
- This is the classic naval game known as Battleship
- The game is also built to have a chat room where players can communicate with each other. 
- Incorporates UDP and TCP elements to perform all functions of the game and the server. 

**Before Execution**

- Before you run the code, the following must be installed

	- Install TKinter framework
	- Install pillow 4.0.0 
		- this is done by calling pip install pillow=4.0.0
	- Install Image 
		- this is done by calling pip install Image

**To Run the Game**

- Run command python main.py in the application directory
- A window should pop up with the ability to input your name
- If you are the host of the game's "lobby" (server) then you will select "New Game" and wait for opponents. 
- if you are joining a game, click "Connect to Game" put the IP and Port of the game you would like to join. Then click "Connect"
- When a game begins, a chat client will open up as well. This will allow all players (not just the ones in your game) to communicate with each other


**Playing the Game**

- Players will play 1v1 games that can be used as a in a tournament style.
- Players click on their opponent's grid to declare attacks. 
- Battleship game remains turn-based.
- With downtime, players can continue to chat with each other. 


**Known Issues**


- To exit game, you must close command line. 
- Not all players are color coordinated.   
