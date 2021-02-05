# TexasHoldEm
Python based Texas HoldEm software which allows the user to play Poker with friends over zoom/skype etc. 

## Short description ##
This code allows the user to play Texas HoldEm with 
friends over over Zoom/Teams/Skype. Only one player 
needs to have a python terminal open. This user 
will input actions (e.g. betting, folding, etc..) 
for all of the players. 

## Game Settup ##
#### Step 1: 
Change the line:
Dropbox_file_root = '/Path/to/your/Dropbox/Folder/'
to the correct path to the Dropbox folder on your 
machine.  (Found on ~ line 150 of this file.) 
Note: technically not strictly required, as the 
program will prompt you for the file path if no 
modification is done. But that will require typing
each time you load a game, and thats boring.  

#### Step 2: 
Run the function LetsPlayCards().

This can either be done on the terminal by running
$ python3 MummeryPoker
or with the following steps
$ python3 
> import MummeryPoker
> MummeryPoker.LetsPlayCards()

(Note: '$' and '>' should not be typed, they denote
terminal prompts. You must be in the same folder
as this file.)

#### Step 3:
The code will generate folders for each player within
the Dropbox file pointed to by the variable Dropbox_file_root.
Within these folders the players will recieve their 
card updates etc. It is **VITALLY IMPORTANT** that the 
players can access this folder. This can be done by 
generating a 'share link' on the Dropbox website. 
Once each player can access their individual dropbox
folders, the game can procceed...

## Game Mechanics 
### 1. Cards/Hands:
For each new hand 2 cards are sent to each player in
a file called UPDATE.txt contained within each players
individual Dropbox folder. The game then follows the 
usual rules of Texas HoldEm. Each user will have to 
click refresh on their UPDATE.txt file to recieve the 
cards from the flop, turn and river. 

### 2. Betting:
Rounds of betting follow the usual rules of Texas HoldEm,
one pre-flop, then one after each of the flop, turn and
river.  At each stage each player has the option to 
check/call/bet/raise/fold (dependent on game situation). 
After making their decision the player will inform the 
user who is running this python script of their choice. 
This (trusted) player then inputs the betting actions of
each player. [Note that Betting summaries are sent to all
players at the end of each betting round so cheating is a
bit of a waste of time.] 

### 3. Showdwon:
At the end of each hand (after the betting round following
the river) any players still in the hand procceeds to the 
showdown. Each players best hand of 5 is calculated from 
their 2 hole cards and 5 communal cards. The best 5 card 
hands of each player are then compared, and the winner 
recieves the betted chips. This file correctly deals with 
both tied hands and multiple pots (which result when one 
or more players are All in).

The hand ranking algorithm can be found within the class 
Score() on line ~ 315 of this file. 

The Showdown algorithm can be found in the showdown() 
function within the Poker() class. (Line ~ 1500.)

### 4. The 'Playing Contract':
A problem with playing on Zoom is players (once they've lost)
backing out of pre-agreed rules regarding renumeration etc.
To prevent this it is possible to have 'Contracts' signed by
all the players before play. If this option is specifed 
(you will be prompted by the program while setting up the game), 
then the game will not begin until all players have 'signed' 
their contract. This involves modifying the final line of the 
file CONTRACT.txt in their dropbox folders. The text of the 
contract can be modified by changing the 'contract_text' 
variables near the top of this file (lines ~ 190). 

## Additional Options 
### 1. Blind structure 
Texas HoldEm involves two enforced bets prior to players
recieving their hole cards. The so-called small and big
'blinds' are either of fixed value for the duration of the 
game, or can vary with hand number. This script gives three
options upon start-up: a. constant value blinds, b. blinds
which double in value every N hands (user specifies N), or 
c. a complete user-specified structure (i.e. blinds = W until
hand number X, then equal Y until hand number Z etc..). 
The user will be prompted for their choice upon start-up.

### 2. Saving/Loading games
If you want to quit before finishing a game then a keyboard
interupt will result in the game automatically being saved.
(The game is also automatically saved upon encountering any
python Error message.) This will produce two files, a 
PlayerFile_ and a GameFile_, which can then be used to re-load
the game at a later point. 

### 3. Playing by email 
If playing by email (not recommended, but possible),
One email account (must be @gmail) is used as a dealer, 
and sends cards, bet summaries, and results of each hand
to player email addresses which  the user specifies. 
All other game mechanics remain the same. 
(Seriously though don't play by email, its much worse.)
