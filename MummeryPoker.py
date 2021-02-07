"""
'Mummrehs Casino Texas HoldEm'

Author: 
Andrew Mummery, 
Oxford University Astrophysics,
andrew.mummery.software@gmail.com 

git repo: https://github.com/andrewmummery/TexasHoldEm

##################################################
############ READ BELOW BEFORE USING #############
##################################################

*** Short description ***
This code allows the user to play Texas HoldEm with 
friends over over Zoom/Teams/Skype. Only one player 
needs to have a python terminal open. This user 
will input actions (e.g. betting, folding, etc..) 
for all of the players. 

*** Game Settup ***
Step 1: Change the line:
Dropbox_file_root = '/Path/to/your/Dropbox/Folder/'
to the correct path to the Dropbox folder on your 
machine.  (Found on ~ line 150 of this file.) 
Note: technically not strictly required, as the 
program will prompt you for the file path if no 
modification is done. But that will require typing
each time you load a game, and thats boring.  

Step 2: Run the function LetsPlayCards().

This can either be done on the terminal by running
$ python3 MummeryPoker
or with the following steps
$ python3 
> import MummeryPoker
> MummeryPoker.LetsPlayCards()

(Note: '$' and '>' should not be typed, they denote
terminal prompts. You must be in the same folder
as this file.)

Step 3:
The code will generate folders for each player within
the Dropbox file pointed to by the variable Dropbox_file_root.
Within these folders the players will recieve their 
card updates etc. It is **VITALLY IMPORTANT** that the 
players can access this folder. This can be done by 
generating a 'share link' on the Dropbox website. 
Once each player can access their individual dropbox
folders, the game can procceed...

*** Game Mechanics ***
1. Cards/Hands:
For each new hand 2 cards are sent to each player in
a file called UPDATE.txt contained within each players
individual Dropbox folder. The game then follows the 
usual rules of Texas HoldEm. Each user will have to 
click refresh on their UPDATE.txt file to recieve the 
cards from the flop, turn and river. 

2. Betting:
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

3. Showdwon:
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

4. The 'Playing Contract':
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

*** Additional Options ***
1. Blind structure 
Texas HoldEm involves two enforced bets prior to players
recieving their hole cards. The so-called small and big
'blinds' are either of fixed value for the duration of the 
game, or can vary with hand number. This script gives three
options upon start-up: a. constant value blinds, b. blinds
which double in value every N hands (user specifies N), or 
c. a complete user-specified structure (i.e. blinds = W until
hand number X, then equal Y until hand number Z etc..). 
The user will be prompted for their choice upon start-up.

2. Saving/Loading games
If you want to quit before finishing a game then a keyboard
interupt will result in the game automatically being saved.
(The game is also automatically saved upon encountering any
python Error message.) This will produce two files, a 
PlayerFile_ and a GameFile_, which can then be used to re-load
the game at a later point. 

3. Playing by email 
If playing by email (not recommended, but possible),
One email account (must be @gmail) is used as a dealer, 
and sends cards, bet summaries, and results of each hand
to player email addresses which  the user specifies. 
All other game mechanics remain the same. 
(Seriously though don't play by email, its much worse.)


""" 

import itertools, random## For the actual game mechanics
import os## For saving and loading game files, and accessing
## dropbox etc.

## For emailing player updates. Might drop from future versions. 
import smtplib, ssl, getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

###### The string below must lead to somewhere within a Dropbox folder
###### on your machine. For example, on my machine it is the following:
###### Dropbox_file_root = '/Users/andrewmummery/Desktop/Dropbox/Poker/'
Dropbox_file_root = '/Path/To/Your/Dropbox/Folder/'

branding = """
____  ____  ___  ___   ____  ____   ____  ____    ________  ______   ___   ___    __    _____  
|   \/   |  | |  | |   |   \/   |   |   \/   |   |   _   |  |   __| |   |  |  |  (  )  |  ___|
| |\  /| |  | |  | |   | |\  /| |   | |\  /| |   |  (_) _|  |  |__  |   |__|  |  /_/   |  |__ 
| | \/ | |  | |  | |   | | \/ | |   | | \/ | |   |  _   \   |   __| |    __   |        |__   |
| |    | |  | |__| |   | |    | |   | |    | |   |  |\   \  |  |__  |   |  |  |         __|  |
|_|    |_|  |______|   |_|    |_|   |_|    |_|   |__| \__|  |_____| |___|  |__|        |_____|

           _______     _________     _____     _      ____   ____     _____  
          |    ___|   |    __   |   |  __|    (_)    |    \  |  |    /     \  
          |   |       |   |__|  |   |  |__     __    |     \ |  |   /   _   \ 
          |   |       |  ____   |   |__   |   | |    |  |\  \|  |  |   (_)   |  
          |   |___    |  |   |  |    __|  |   | |    |  | \     |   \       /
          |_______|   |__|   |__|   |_____|   |_|    |__|  \____|    \_____/
                         
                                                  
"""

# ***** THE PLAYER CONTRACT ******
#
# The default contract will look something like this. 
# contract = """{branding}
#
# I, {player_name}, hereby agree to the rules of Mummrehs Casino Texas Holdem:
#
# CONTRACT_MAIN_BODY
#
# CONTRACT_MONEY_RULES
#
# Signed:"""
#
# edit contract_main_body and contract_money_rules below to 
# create your own contract. Leave either/both as a blank strings 
# if you don't want contracts. 

contract_main_body = """
                1. Andy has produced fair and unbiased Poker software. I will therefore not blame Andy when I perform poorly/he beats me.

                2. I actually understand the rules of Texas Holdem. (If not: https://en.wikipedia.org/wiki/Texas_hold_%27em#Rules)

                3. I understand that if do not show up to a scheduled game I automatically come last. (Pete this is for you.)

                4. That this game is played for real cash moneys, with the following structure:
"""

contract_money_rules = """
                      a. The player who comes last pays £10 to the beer kitty.
                      b. The player who comes second last pays £5 to the beer kitty.
                      c. The player who comes second pays £2 to the beer kitty.
                      d. The player who comes first pays £1 to the beer kitty.
"""

contract_money_rules = """
                      a. The player who comes last pays £7 to the beer kitty.
                      b. The player who comes second pays £4 to the beer kitty.
                      d. The player who comes first pays £2 to the beer kitty.
"""


def LetsPlayCards():
    print(branding)
    new_or_load = ''
    while new_or_load not in ['n', 'l']:
        new_or_load = input('Would you like to play a new game (n), or load an old game (l)? ')
    if new_or_load == 'n':
        blindStructure = ''
        while blindStructure not in ['t', 'f']:
            blindStructure = input('Play with a blind structure (t), or simple constant blinds (f)? ')
        if blindStructure == 't':
            blindStructure = True
        else:
            blindStructure = False
        
        game_name = input('Input name for this game: ')
        
        email_or_dropbox = ''
        while email_or_dropbox not in ['d', 'e']:
            email_or_dropbox = input('Would you like to play this game via dropbox (d) <--- HIGHLY RECOMMENDED, or email (e)? ')
                
        game = Poker(blindStructure=blindStructure, game_name=game_name, email_or_dropbox=email_or_dropbox)
        try:
            game.play_game()
        except KeyboardInterrupt:
            print('\nPlayer quits! ')
            print('Saving progres....')
            game.save_game()
            quit()            
        except Exception as e:
            print('\nEncountered an Error: %s '%e)
            print('Saving progres....')
            game.save_game()
            quit()
    else:
        game_name = input('Input name used for this game: ')
        game = Poker(load_from_file=True, game_name=game_name)
        try:
            game.play_game()
        except KeyboardInterrupt:
            print('\nPlayer quits! ')
            print('Saving progres....')
            game.save_game()
            quit()            
        except Exception as e:
            print('\nEncountered an Error: %s '%e)
            print('Saving progres....')
            game.save_game()
            quit()
    return None


class Card(object):
    RANKS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    SUITS = ('Spades', 'Diamonds', 'Hearts', 'Clubs')

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):## Allows convenient printing of the Cards. 
        if self.rank == 14:
            rank = 'Ace'
        elif self.rank == 13:
            rank = 'King'
        elif self.rank == 12:
            rank = 'Queen'
        elif self.rank == 11:
            rank = 'Jack'
        else:
            rank = self.rank
        return str(rank) + ' of ' + self.suit

    def __eq__(self, other):## Allows the hands to be sorted 
        return (self.rank == other.rank)

    def __ne__(self, other):## Allows the hands to be sorted 
        return (self.rank != other.rank)

    def __lt__(self, other):## Allows the hands to be sorted 
        return (self.rank < other.rank)

    def __le__(self, other):## Allows the hands to be sorted 
        return (self.rank <= other.rank)

    def __gt__(self, other):## Allows the hands to be sorted 
        return (self.rank > other.rank)

    def __ge__(self, other):## Allows the hands to be sorted 
        return (self.rank >= other.rank)
   

class Deck(object):
    def __init__(self):
        self.deck = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                card = Card(rank, suit)
                self.deck.append(card)

    def shuffle(self):
        random.shuffle(self.deck)

    def __len__(self):
        return len(self.deck)

    def deal(self):
        if len(self) == 0:
            return None
        else:
            return self.deck.pop()


class Score(object):
    
    def __init__(self, hand): 
        self.hand = hand
        self.total_point = 0
        self.hand_type = ''
        self.get_score()
    
    def get_score(self):
        self.straight_flush(self.hand)
    
    def base_score(self):
        ''' Offsets each hand type in value (so no high card can beat a pair etc.) '''
        return 14**5 + 14**4 + 14**3 + 14**2 + 14
    
    def straight_flush(self, hand):
        ''' This is a straight flush. '''
        sortedHand=sorted(hand,reverse=True)
        k=8
        iv = k * self.base_score()
        total_point = iv
        flag = True
        current_suit=sortedHand[0].suit
        current_rank=sortedHand[0].rank
        for card in sortedHand:
            if card.suit!=current_suit:
                flag=False
                break
            elif card.rank!=current_rank:
                if card.rank == 5 and current_rank == 13:## Ace, 5, 4, 3, 2 is a valid straight. 
                    current_rank = 4
                else:
                    flag=False
                    break                
            else:
                current_rank-=1
        if flag:
            self.hand_type= 'Straight Flush'
            for i, card in enumerate(sortedHand):
                total_point += card.rank * 14**(4-i)
            self.total_point = total_point
        else:
            self.four_of_a_kind(sortedHand)
        
        
    def four_of_a_kind(self, hand):
        ''' This is a four of a kind. '''
        sortedHand=sorted(hand,reverse=True)
        k=7
        iv = k * self.base_score()
        total_point = iv
        Currank=sortedHand[1].rank#since it has 4 identical ranks, the 2nd one in the sorted list must be the identical rank
        count=0
        for card in sortedHand:
            if card.rank==Currank:
                count+=1
        if count==4:
            self.hand_type='Four of a Kind'
            card_ranks = []
            for card in sortedHand:
                card_ranks.append(card.rank)
            quad_cards = []
            non_quad_cards = []
            for i, cardrank in enumerate(card_ranks):
                if cardrank  in card_ranks[i+1:]:
                    if cardrank not in quad_cards:
                        quad_cards.append(cardrank)
                elif cardrank in quad_cards:
                    continue
                else:
                    non_quad_cards.append(cardrank)
            total_point += quad_cards[0]*14 + non_quad_cards[0]
            self.total_point = total_point
        else:
            self.full_house(sortedHand)
        
        
    def full_house(self, hand):
        ''' This is a full house. '''
        sortedHand=sorted(hand,reverse=True)
        k=6
        iv = k * self.base_score()
        total_point = iv
        card_ranks=[]
        for card in sortedHand:
            card_ranks.append(card.rank)
        rank1=sortedHand[0].rank#The 1st rank and the last rank will be different in a sorted list of a full house
        rank2=sortedHand[-1].rank
        num_rank1=card_ranks.count(rank1)
        num_rank2=card_ranks.count(rank2)
        if (num_rank1==2 and num_rank2==3):
            self.hand_type='Full House'
            total_point += rank2 * 14 + rank1
            self.total_point = total_point
        elif (num_rank1==3 and num_rank2==2):
            self.hand_type='Full House'
            total_point += rank1 * 14 + rank2
            self.total_point = total_point
        else:
            self.flush(sortedHand)
        
        
    def flush(self, hand):
        ''' This is a flush. '''
        sortedHand=sorted(hand,reverse=True)
        k=5
        iv = k * self.base_score()
        total_point = iv
        flag=True
        current_suit=sortedHand[0].suit
        for card in sortedHand:
            if card.suit!=current_suit:
                flag=False
                break
        if flag:
            self.hand_type='Flush'
            for i, card in enumerate(sortedHand):
                total_point += card.rank * 14**(4-i)
            self.total_point = total_point
        else:
            self.straight(sortedHand)
        
        
    def straight(self, hand):
        ''' This is a straight. 
        '''   
        sortedHand=sorted(hand,reverse=True)
        k=4
        iv = k * self.base_score()
        total_point = iv
        flag=True
        current_rank=sortedHand[0].rank                        
        for card in sortedHand:
            if card.rank!=current_rank:
                if card.rank == 5 and current_rank == 13:## Ace, 5, 4, 3, 2 is a valid straight. 
                    current_rank = 4
                else:
                    flag=False
                    break
            else:
                current_rank-=1
        if flag:
            self.hand_type='Straight'
            for i, card in enumerate(sortedHand):
                total_point += card.rank * 14**(4-i)
            self.total_point = total_point
        else:
            self.three_of_a_kind(sortedHand)
        
        
    def three_of_a_kind(self, hand):
        ''' This is a three of a kind. 
        '''   
        sortedHand=sorted(hand,reverse=True)
        k=3
        iv = k * self.base_score()
        total_point = iv
        trip_rank=sortedHand[2].rank                    #In a sorted rank, the middle one will have 3 counts if three of a kind
        card_ranks=[]
        for card in sortedHand:
            card_ranks.append(card.rank)
        if card_ranks.count(trip_rank)==3:
            self.hand_type="Three of a Kind"
            trip_cards = []
            non_trip_cards = []
            for i, cardrank in enumerate(card_ranks):
                if cardrank in card_ranks[i+1:]:
                    if cardrank not in trip_cards:
                        trip_cards.append(cardrank)
                elif cardrank in trip_cards:
                    continue
                else:
                    non_trip_cards.append(cardrank)
            total_point += trip_cards[0]*14**2 + non_trip_cards[0] * 14 + non_trip_cards[1]
            self.total_point = total_point
        else:
            self.two_pair(sortedHand)
        
        
    def two_pair(self, hand):
        ''' This is the two pair. 
        '''   
        sortedHand=sorted(hand,reverse=True)
        k=2
        iv = k * self.base_score()
        total_point = iv
        rank1=sortedHand[1].rank                        #in a five cards sorted group, if isTwo(), the 2nd and 4th card will have another identical rank
        rank2=sortedHand[3].rank
        card_ranks=[]
        for card in sortedHand:
            card_ranks.append(card.rank)
        if card_ranks.count(rank1)==2 and card_ranks.count(rank2)==2:
            self.hand_type="Two Pair"
            pair_cards = []
            non_pair_cards = []
            for i, cardrank in enumerate(card_ranks):
                if cardrank in card_ranks[i+1:]:
                    if cardrank not in pair_cards:
                        pair_cards.append(cardrank)                        
                elif cardrank in pair_cards:
                    continue
                else:
                    non_pair_cards.append(cardrank)
            total_point += pair_cards[0] * 14**2 + pair_cards[1] * 14 + non_pair_cards[0]
            self.total_point = total_point
        else:
            self.one_pair(sortedHand)
        
        
    def one_pair(self, hand):
        ''' This is the pair. 
        '''   
        sortedHand=sorted(hand,reverse=True)
        k=1
        iv = k * self.base_score()
        total_point = iv
        card_ranks=[]                                      #create an empty list to store ranks
        card_count=[]                                      #create an empty list to store number of count of each rank
        for card in sortedHand:
            card_ranks.append(card.rank)
        for each in card_ranks:
            count=card_ranks.count(each)
            card_count.append(count)
        if card_count.count(2)==2 and card_count.count(1)==3:  #There should be only 2 identical numbers and the rest are all different
            self.hand_type="One Pair"
            pair_cards = []
            non_pair_cards = []
            for i, cardrank in enumerate(card_ranks):
                if cardrank in card_ranks[i+1:]:
                    if cardrank not in pair_cards:
                        pair_cards.append(cardrank)
                elif cardrank in pair_cards:
                    continue
                else:
                    non_pair_cards.append(cardrank)
            for i in range(3):
                total_point += non_pair_cards[i]**(3-i)
            total_point += pair_cards[0]**3
            self.total_point = total_point  
        else:
            self.high_card(sortedHand)
           
    def high_card(self, hand):
        ''' evaluates the score for a high card, 
            if we get to this point then the hand is none of the other types. '''
        sortedHand=sorted(hand,reverse=True)
        k=0
        iv = k * self.base_score()
        total_point = iv
        for i, card in enumerate(sortedHand):
            total_point += card.rank * 14**(4-i)
        self.hand_type="High Card"
        self.total_point = total_point


class Player(object):
    def __init__(self, chips=None, hole_cards=None, player_name=None, player_email=None, best_hand=None, numCardHole=2, numCardHand=5, isDealer=False,
        betted_this_round=0, betted_this_hand=0, hasFolded=False, isAllIn=False):
        self.player_name = player_name
        self.player_email = player_email
        self.chips = chips
        self.hole_cards = hole_cards
        self.best_hand = best_hand
        self.numCardHole = numCardHole### Defaults to TexasHoldEm rules.
        self.numCardHand = numCardHand### Defaults to TexasHoldEm rules.
        self.isDealer = isDealer
        self.betted_this_round = betted_this_round
        self.betted_this_hand = betted_this_hand
        self.hasFolded = hasFolded
        self.isAllIn = isAllIn
            
    def deal_hole_cards(self, deck):
        # print('\nPlayer %s Hand: '%(self.player_name))
        hole_cards = []
        for i in range(self.numCardHole):
            card = deck.deal()
            hole_cards.append(card)
            # print(str(card))
        self.hole_cards = hole_cards
    
    def possibleHands(self, all_cards):
        ''' returns all the cobinations of length n_hand from a list of all_cards (of length(all_cards) > n_hand) '''
        if len(all_cards) < self.numCardHand:
            return None
        elif len(all_cards) == self.numCardHand:
            return all_cards
        return list(itertools.combinations(all_cards, self.numCardHand))
    
    
    def get_best_hand(self, possible_cards):
        possible_hands = self.possibleHands(possible_cards)
        hand_scores = []
        hand_types = []
        for hand in possible_hands:
            Hand = Score(hand)
            s = Hand.total_point
            t = Hand.hand_type
            hand_scores.append(s)
            hand_types.append(t)

        maxpoint=max(hand_scores)
        maxindex=hand_scores.index(maxpoint)
        self.best_hand = [sorted(possible_hands[maxindex], reverse=True), hand_scores[maxindex], hand_types[maxindex]]
    

class Pot(object):
    def __init__(self, total_value = 0, betted_this_round = 0, highestBet = 0, numRaises = 0, smallBlindIndex = 0, bigBlindIndex = 0):
        self.total_value = total_value
        self.betted_this_round = betted_this_round
        self.highestBet = highestBet
        self.numRaises = numRaises
        self.smallBlindIndex = smallBlindIndex
        self.bigBlindIndex = bigBlindIndex


class Poker(object):
    def __init__(self, players=None, deck=None, pot=None, smallBlindValue=None, bigBlindValue=None, blindStructure=False, 
        game_type='TexasHoldEm', numHand=0, game_name='MummrehCasinosTexasHoldEm', load_from_file=False, email_or_dropbox='d'):
        if game_type == 'TexasHoldEm':
            self.numCardHole = 2
            self.numCardFlop = 3
            self.numCardTurn = 1
            self.numCardRiver = 1
            self.numCardHand = 5
            self.game_type = game_type
            self.game_name = game_name
        else:
            raise ValueError('Only TexasHoldEm is currently implemented. ')            
        
        self.email_or_dropbox = email_or_dropbox
        
        if load_from_file:
            try:
                print('Trying to load game from files with game name = %s ......  '%self.game_name)
                self.load_game(self.game_name)
                print('Success. \n')
            except ValueError:## Couldn't find the game under the assumption file_name = game_name
                print('Failed. ')
                print('\n Loading a game from a text file ...... ')
                print(' Files should be of the format PlayerFile_YOURFILENAME.txt and GameFile_YOURFILENAME.txt')
                load_file_name = input('What is YOURFILENAME for the two files?  ')
                self.load_game(load_file_name)                
        else:
            if players is None:
                players = []
                numPlayers = eval(input('How many players are there? '))## Make this more robust. 
                for i in range(numPlayers):
                    print('\nFor player %d please input: '%(i+1))
                    player_name = input('Player Name: ')
                    if self.email_or_dropbox == 'e':
                        player_email = input('Player email: ')
                    else:
                        player_email = 'N/A'
                    player_pot = ''
                    while not player_pot.isnumeric():                        
                        player_pot = input('Inital number of chips: ')
                    player_pot = eval(player_pot)
                    player = Player(player_name=player_name, player_email=player_email, chips=player_pot, numCardHole=self.numCardHole,
                    numCardHand=self.numCardHand)
                    players.append(player)
                
            self.players = players
            self.numPlayers = len(players)
        
            if deck is None:
                self.deck = Deck()
                self.deck.shuffle()
            else:
                self.deck = deck
        
            self.pot = pot## Will be initialised within the round_of_betting function.
        
            if smallBlindValue is not None:
                self.smallBlindValue = smallBlindValue
            else:
                smallBlind = ''
                while not smallBlind.isnumeric():
                    smallBlind = input('What is the value of the initial small blind? ')
                self.smallBlindValue = eval(smallBlind)
        
            if bigBlindValue is not None:            
                self.bigBlindValue = bigBlindValue
            else:
                bigBlind = ''
                while not bigBlind.isnumeric():
                    bigBlind = input('What is the value of the initial big blind? ')
                self.bigBlindValue = eval(bigBlind)
        
            if blindStructure:
                print('\nYou have elected to specify a blind structure. ')
                print('You have the option to double the small and big blinds every N rounds (option = double, you will specify N)')
                print('or you can specify how the blinds change (option = user specifed). ', end='')
                print('i.e. after hand 10, small blind = X, big blind = Y; after hand 20 etc.. You will prompted for more instructions. ' )
                blind_type = ''
                while blind_type not in ['s', 'd']:
                    blind_type = input('\nBlinds type double (d), or user specified (s)? ')
                self.blind_type = blind_type
                if blind_type == 'd':
                    numHandToDouble = ''
                    while not numHandToDouble.isnumeric():
                        numHandToDouble = input('The blinds will double every N hands. Please specify N = ? ')
                    self.numHandToDouble = eval(numHandToDouble)
                elif blind_type == 's':
                    blinds = []### Will be a list of numHandToChange, newSmallBlind, newBigBlind
                    while True:
                        numHandToChange = ''
                        newSmallBlind = ''
                        newBigBlind = ''
                        while not numHandToChange.isnumeric():
                            numHandToChange = input('Specify hand to change every blinds: (d = ALL DONE) ')
                            if numHandToChange == 'd':
                                break
                        if numHandToChange == 'd':
                            break
                        else:
                            numHandToChange = eval(numHandToChange)
                        while not newSmallBlind.isnumeric():
                            newSmallBlind = input('Specify new small blind at hand %d: '%(numHandToChange))
                        newSmallBlind = eval(newSmallBlind)
                        while not newBigBlind.isnumeric():
                            newBigBlind = input('Specify new big blind at hand %d: '%(numHandToChange))
                        newBigBlind = eval(newBigBlind)
                    
                        blinds.append([numHandToChange, newSmallBlind, newBigBlind])
                    self.blinds = blinds
        
            self.blindStructure = blindStructure
            self.numHand = numHand
        
        # End. 
    
    def save_game(self):
        ''' Saves a CSV file of the game & player properties. 
        
            Player file save format is: 
            
            Player 1: name, email, chips, isDealer
            Player 2: ....
        
            Game save file format is:
            email_or_dropbox
            numHand
            player names: player1_name, ....
            smallBlindValue
            bigBlindValue
            blindStructure (dependent on current user choice of blindStructure.)
        '''
        player_save_name = 'PlayerFile_%s.txt'%self.game_name
        game_save_name = 'GameFile_%s.txt'%self.game_name
        k=0
        while (os.path.isfile(player_save_name)) or (os.path.isfile(game_save_name)):
            k+=1
            if k == 1:
                player_save_name = player_save_name[:-4]
            else:
                player_save_name = player_save_name[:-6]
            player_save_name = player_save_name + '_' + str(k)
            player_save_name = player_save_name + '.txt'  
            if k == 1:
                game_save_name = game_save_name[:-4]
            else:
                game_save_name = game_save_name[:-6]
            game_save_name = game_save_name + '_' + str(k)
            game_save_name = game_save_name + '.txt'
            
        
        with open(player_save_name, 'w+') as player_save_file:
            line0 = '## %s     %s      %s      %s \n'%('Name', 'Email', 'Chips', 'isDealer')
            player_save_file.write(line0)
            for player in self.players:
                line_string = '%s     %s     %s      %s \n'%(
                player.player_name, player.player_email, player.chips+player.betted_this_round+player.betted_this_hand, player.isDealer)
                player_save_file.write(line_string)
        
        with open(game_save_name, 'w+') as game_save_file:
            line_ = self.email_or_dropbox+'\n'
            game_save_file.write(line_)            
            line0 = '%s\n'%self.numHand
            game_save_file.write(line0)            
            line1 = 'Players: '
            for player in self.players:
                line1 = line1 + '   %s'%player.player_name
            game_save_file.write(line1+'\n')
            line2 = '%s\n'%self.smallBlindValue
            game_save_file.write(line2)
            line3 = '%s\n'%self.bigBlindValue
            game_save_file.write(line3)
            line4 = str(self.blindStructure)+'\n'
            game_save_file.write(line4)
            if self.blindStructure:
                line5 = self.blind_type+'\n'
                game_save_file.write(line5)
                if self.blind_type == 'd':
                    line6 = str(self.numHandToDouble)+'\n'
                    game_save_file.write(line6)                    
                elif self.blind_type == 's':
                    for blind in self.blinds:
                        line_ = ''
                        for item in blind:
                            line_ = line_ + '%s   '%item
                        game_save_file.write(line_+'\n')
            
            
        return None
    
    def load_game(self, load_file_name):
        ''' Loads text files of the game & player properties. 
            I should only be used initialising a game. 
        '''
        player_load_name = 'PlayerFile_%s.txt'%load_file_name
        game_load_name = 'GameFile_%s.txt'%load_file_name
        if not (os.path.isfile(player_load_name) and os.path.isfile(game_load_name)):
            raise ValueError('Either the game file or player file does not exist. \n Trying: Game File = %s \n Player File = %s'
            %(game_load_name, player_load_name))
        
        ## Load player profiles
        players = []
        with open(player_load_name, 'r') as player_load_file:
            for i, line in enumerate(player_load_file):
                if i != 0:
                    player_name = line.split()[0]
                    player_email = line.split()[1]
                    player_chips = int(line.split()[2])
                    if line.split()[3] == 'False':
                        player_isDealer = False
                    elif line.split()[3] == 'True':
                        player_isDealer = True
                    player = Player(player_name=player_name, player_email = player_email, chips=player_chips, isDealer = player_isDealer)
                    players.append(player)
        
        self.players = players
        self.numPlayers = len(players)
        
        ## Load game stats
        blinds = []## might be needed.
        with open(game_load_name, 'r') as game_load_file:
            for j, line in enumerate(game_load_file):
                i = j - 1## I changed the save structure after coding this and I cba changing it.
                if i == -1:
                    self.email_or_dropbox = line.split()[0]
                if i == 0:
                    self.numHand = int(line.split()[0])
                elif i == 1:
                    continue
                elif i == 2:
                    self.smallBlindValue = int(line.split()[0])
                elif i == 3:
                    self.bigBlindValue = int(line.split()[0])
                elif i == 4:
                    if line.split()[0] == 'False':
                        self.blindStructure = False
                    elif line.split()[0] == 'True':
                        self.blindStructure = True
                elif i == 5:
                    ## Should only be here if there is a blindStructure
                    if self.blindStructure:
                        self.blind_type = line.split()[0]
                elif i >= 6:
                    if self.blind_type == 'd':
                        self.numHandToDouble = int(line.split()[0])
                    elif self.blind_type == 's':
                        blind = []
                        for item in line.split():
                            blind.append(int(item))
                        blinds.append(blind)

        if self.blindStructure:
            if self.blind_type == 's':
                self.blinds = blinds                    
        return None
        
    def play_game(self):
        ''' Plays a game of Texas HoldEm. 
        '''
        global Dropbox_file_root
        
        if not any(player.isDealer for player in self.players):
            self.players[0].isDealer = True
        if self.numPlayers > 23:
            raise ValueError('Too many players (or equivalently, not enough cards). ')
        
        if self.email_or_dropbox == 'e':
            self.configure_dealer_email()
            self.send_start_up_email()
        else:
            if Dropbox_file_root == '/Path/To/Your/Dropbox/Folder/':
                Dropbox_file_root = input('Input the file path to a location within your Dropbox foler: ')
            if not os.path.isdir(Dropbox_file_root):
                raise ValueError('Incorrect dropbox file path. ')
            self.configure_dropbox_folders()
            self.dropbox_start_up()
            player_contracts = ''
            while player_contracts not in ['y', 'n']:
                player_contracts = input('Require players to sign contracts before playing? (y/n)  ')
            did_that_work = ''
            while did_that_work != 'y':
                did_that_work = input('Share dropbox links with fellow players. Enter "y" when all players are ready. ')
                if did_that_work == 'y':
                    if player_contracts == 'y':
                        count = 0#### ADD THIS AS AN OPTIONAL EXTRA? MIGHT NOT REQUIRE THE CONTRACT.
                        for player in self.players:
                            with open(Dropbox_file_root+player.player_name+'/CONTRACT'+'.txt', 'r') as test_file:
                                lines = test_file.read().splitlines()
                                last_line = lines[-1].split()
                                if last_line != ['Signed:']:
                                    count += 1
                                    print(lines[-1].lstrip())
                                else:
                                    print('%s has not signed the contract!'%player.player_name)
                        if not count == self.numPlayers:
                            did_that_work = 'n'
                
        
        for player in self.players:            
            if not os.path.isfile(Dropbox_file_root+player.player_name+'/GAMELOG'+'.txt'): 
                with open(Dropbox_file_root+player.player_name+'/GAMELOG'+'.txt', 'w+') as test_file:
                    test_file.write(branding)
        
        while True:
            deck = Deck()
            deck.shuffle()
            self.deck = deck
            self.numHand += 1
            
            ### Update small and big blinds if playing with
            ### a blind structure. 
            if self.blindStructure:
                if self.blind_type == 'd':
                    if self.numHand % self.numHandToDouble == 0:
                        self.smallBlindValue += self.smallBlindValue
                        self.bigBlindValue += self.bigBlindValue
                elif self.blind_type == 's':
                    for blind in self.blinds:
                        if self.numHand == blind[0]:
                            self.smallBlindValue = blind[1]
                            self.bigBlindValue = blind[2]
            ###
            
            ### Plays a hand.
            self.play_hand()
            ###
            
            ### Remove players who have run out of chips. 
            prev_player = None## for determining dealer status.
            for ind, player in enumerate(self.players[::-1]):#going through backwards helps
                if player.chips > 0:
                    prev_player = player 
                    continue
                else:
                    if player.isDealer:
                        if (ind == 0) or (prev_player is None):
                            self.players[-1].isDealer = True
                        else:
                            prev_player.isDealer = True
                    print('\n%s is out of the game! '%player.player_name)
                    """ #############################################################
                        Could add buy-back here. Also would be good to update game-log
                        with PlayerOut or something. Should make a list of players who 
                        have gone out.
                        #############################################################
                    """
                    message = '\n================================================================================================\n'
                    message += '\n%s IS OUT OF THE GAME. \n'%player.player_name
                    for player_ in self.players: 
                        with open(Dropbox_file_root+player_.player_name+'/GAMELOG'+'.txt', 'a') as test_file:#a for append.
                            test_file.write(message)
                            
                    self.players.remove(player)## Removes the player from the players list
                    self.numPlayers += -1## Ensures betting round logic correct.
                    
            if self.numPlayers == 1:
                print('\n%s is the Winner!! '%(self.players[0].player_name))
                message = '\n================================================================================================\n'
                message += '\n%s IS THE WINNER. \n'%self.players[0].player_name
                message += '\n\n\n\n\n End. '
                for player_ in self.players: 
                    with open(Dropbox_file_root+player_.player_name+'/GAMELOG'+'.txt', 'a') as test_file:#a for append.
                        test_file.write(message)
                
                break## Could add a ranking/scoring summary here.
            ###
            
            
            ### Resets player properties before starting next round. 
            for ind, player in enumerate(self.players):
                player.betted_this_round = 0
                player.betted_this_hand = 0
                player.isAllIn = False
                player.hasFolded = False                    
                player.hole_cards = None
                player.best_hand = None
                if player.isDealer:
                    index = ind
            
            self.players[index].isDealer = False
            self.players[(index+1) % self.numPlayers].isDealer = True    
            ###
            
            
            ### Asks if you want to proceed to next hand, if not gives opportunity
            ### to save game status. 
            next_hand = ''
            next_hand = input('Play next hand? (yes = any key; no = n) ')
            if next_hand == 'n':
                save_game_status = ''
                while save_game_status not in ['y', 'n', 'p']:
                    save_game_status = input('Would you like to save the game status? (y/n), or play next hand (p): ')
                if save_game_status  == 'y':
                    self.save_game()
                    break
                elif save_game_status == 'p':
                    pass
                else:## 'n' was selected.
                    break
            ###
            
            
        # End. 
    
    def play_hand(self):
        ''' Play a hand of Texas HoldEm. '''
        bet_summaries = []
        for player in self.players:
            player.deal_hole_cards(self.deck)
        
        if self.email_or_dropbox == 'e':        
            self.email_card_update()
        else:
            self.dropbox_update()
        
        bet_summary = self.round_of_betting(preFlop=True)
        bet_summaries.append(bet_summary)
        
        if self.email_or_dropbox == 'e':
            self.email_bet_summary(bet_summary)
        else:
            self.dropbox_update(bet_summaries=bet_summaries)
        
        flop = []
        turn = []
        river = []

        print('\nFlop: ')
        for i in range(self.numCardFlop):
            card = self.deck.deal()
            flop.append(card)
            print(str(card))
        
        if self.email_or_dropbox == 'e':
            self.email_card_update(flop=flop)
        else:
            self.dropbox_update(flop=flop, bet_summaries=bet_summaries)
        
        bet_summary = self.round_of_betting()
        bet_summaries.append(bet_summary)
        
        if self.email_or_dropbox == 'e':
            self.email_bet_summary(bet_summary)
        else:
            self.dropbox_update(flop=flop, bet_summaries=bet_summaries)
                
        print('\nTurn: ')
        for i in range(self.numCardTurn):
            card = self.deck.deal()
            turn.append(card)
            print(str(card))
        
        if self.email_or_dropbox == 'e':       
            self.email_card_update(flop=flop, turn=turn)
        else:
            self.dropbox_update(flop=flop, turn=turn, bet_summaries=bet_summaries)
        
        bet_summary = self.round_of_betting()
        bet_summaries.append(bet_summary)
        
        if self.email_or_dropbox == 'e':
            self.email_bet_summary(bet_summary)
        else:
            self.dropbox_update(flop=flop, turn=turn, bet_summaries=bet_summaries)
        
        print('\nRiver: ')
        for i in range(self.numCardRiver):
            card = self.deck.deal()
            river.append(card)
            print(str(card))
        
        if self.email_or_dropbox == 'e':        
            self.email_card_update(flop=flop, turn=turn, river=river)
        else:
            self.dropbox_update(flop=flop, turn=turn, river=river, bet_summaries=bet_summaries)
        
        bet_summary = self.round_of_betting()
        bet_summaries.append(bet_summary)
        
        if self.email_or_dropbox == 'e':
            self.email_bet_summary(bet_summary)
        else:
            self.dropbox_update(flop=flop, turn=turn, river=river, bet_summaries=bet_summaries)        
        
        showdown_summary = self.showdown(flop, turn, river)
        
        if self.email_or_dropbox == 'e':
            self.email_showdown_summary(showdown_summary)
        else:
            self.dropbox_showdown_summary(showdown_summary, bet_summaries)
        
        if self.email_or_dropbox == 'd':
            self.dropbox_update_game_log(flop, turn, river)
        # End.     
                
    def round_of_betting(self, preFlop=False):
        bet_count = 0
        bet_summary = 'Betting round summary: \n'## Will be updated with each action. 
        num_players_who_can_bet = self.numPlayers
        for player in self.players:
            if player.hasFolded or player.isAllIn:
                num_players_who_can_bet += - 1
        if preFlop:
            self.pot = Pot()## Initialise/re-write to an empty pot. 
            for i, player in enumerate(self.players):
                if player.isDealer:
                    break
            smallBlindIndex = (i+1) % self.numPlayers
            bigBlindIndex = (i+2) % self.numPlayers
            self.pot.smallBlindIndex = smallBlindIndex
            self.pot.bigBlindIndex = bigBlindIndex
            
            ## Small blind bets
            print('\n %s is the small blind and bets %d chips, they now have %d chips remaining. '
            %(self.players[self.pot.smallBlindIndex].player_name, 
            min(self.smallBlindValue, self.players[self.pot.smallBlindIndex].chips),
            self.players[self.pot.smallBlindIndex].chips - min(self.smallBlindValue, self.players[self.pot.smallBlindIndex].chips)))
            
            this_bet = ('\n%s'%self.players[self.pot.smallBlindIndex].player_name).ljust(25)
            this_bet += 'SMALL BLIND'
            this_bet = this_bet.ljust(50)
            this_bet += 'bet value = %d chips. '%(min(self.smallBlindValue, self.players[self.pot.smallBlindIndex].chips))
            this_bet = this_bet.ljust(75)
            bet_summary += this_bet
            
            self.pot.betted_this_round += min(self.smallBlindValue, self.players[self.pot.smallBlindIndex].chips)
            self.players[self.pot.smallBlindIndex].betted_this_round += min(self.smallBlindValue, self.players[self.pot.smallBlindIndex].chips)
            self.players[self.pot.smallBlindIndex].chips += - min(self.smallBlindValue, self.players[self.pot.smallBlindIndex].chips)
            if self.players[self.pot.smallBlindIndex].chips == 0:
                print('ALL IN!')
                self.players[self.pot.smallBlindIndex].isAllIn = True
                bet_summary += '\n%s ALL IN.'%self.players[self.pot.smallBlindIndex].player_name
            
            
            ## Big blind bets
            print('\n %s is the big blind and bets %d chips, they now have %d chips remaining. '
            %(self.players[self.pot.bigBlindIndex].player_name, 
            min(self.bigBlindValue, self.players[self.pot.bigBlindIndex].chips),
             self.players[self.pot.bigBlindIndex].chips - min(self.bigBlindValue, self.players[self.pot.bigBlindIndex].chips)))
            
            this_bet = ('\n%s'%self.players[self.pot.bigBlindIndex].player_name).ljust(25)
            this_bet += 'BIG BLIND'
            this_bet = this_bet.ljust(50)
            this_bet += 'bet value = %d chips. '%(min(self.bigBlindValue, self.players[self.pot.bigBlindIndex].chips))
            this_bet = this_bet.ljust(75)
            bet_summary += this_bet
             
            self.pot.betted_this_round += min(self.bigBlindValue, self.players[self.pot.bigBlindIndex].chips)
            self.players[self.pot.bigBlindIndex].betted_this_round += min(self.bigBlindValue, self.players[self.pot.bigBlindIndex].chips)
            self.players[self.pot.bigBlindIndex].chips += - min(self.bigBlindValue, self.players[self.pot.bigBlindIndex].chips)
            if self.players[self.pot.bigBlindIndex].chips == 0:
                print('ALL IN!')
                self.players[self.pot.bigBlindIndex].isAllIn = True
                bet_summary += '\n%s ALL IN.'%self.players[self.pot.bigBlindIndex].player_name                
            
            self.pot.highestBet = self.bigBlindValue
            while True:
                for i in range(self.pot.smallBlindIndex + 2, self.pot.smallBlindIndex + self.numPlayers + 2):
                    if bet_count == self.numPlayers:
                        break
                    if num_players_who_can_bet <= 1:
                        bet_summary += '%d player remains able to bet. '%(num_players_who_can_bet)
                        break
                    end_str = ''# formatting
                    ind = i % self.numPlayers
                    player_to_bet = self.players[ind]
                    action = 0# These three initalisations are there
                    bet_value = ' '#so that only valid input is taken from the user (ints for bets and raises)
                    raise_value = ' '# and strings for actions. This ensures typos dont break the code.
                    ### On pre-flop everyone has to raise, call or fold. As the blinds have already betted.
                    if (not player_to_bet.hasFolded) and (not player_to_bet.isAllIn):
                        call_value = self.pot.highestBet - player_to_bet.betted_this_round 
                        if call_value >= player_to_bet.chips:
                            while action not in ['a', 'f']:
                                print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                action = input('Would you like to go ALL IN (a, cost = %d chips) or FOLD (f)? '
                                %player_to_bet.chips)
                        elif self.pot.numRaises < 3: 
                            while action not in ['r', 'c', 'f']:
                                print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                action = input('Would you like to RAISE (r, cost = %d + raise value chips), CALL (c, cost = %d chips) or FOLD (f)? '
                                %(call_value, call_value))
                        else:
                            while action not in ['c', 'f']:
                                print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                action = input('Would you like to CALL (c, cost = %d chips) or FOLD (f)? '
                                %(call_value))
                        if action == 'a':
                            bet_value = player_to_bet.chips
                            print('ALL IN.')
                            player_to_bet.isAllIn = True
                            bet_count += 1
                            self.pot.betted_this_round += bet_value
                            player_to_bet.chips += - bet_value
                            player_to_bet.betted_this_round += bet_value
                            this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                            this_bet += 'ALL IN'
                            this_bet = this_bet.ljust(50)
                            this_bet += 'bet_value = %d chips. '%bet_value
                            this_bet = this_bet.ljust(75)
                            bet_summary += this_bet + end_str
                        elif action == 'r':
                            while not raise_value.isnumeric():                                
                                raise_value = input('Raise by how much? (cost = %d + raise value chips) '%(call_value))
                            raise_value = eval(raise_value)
                            if call_value + raise_value >= player_to_bet.chips:
                                print('ALL IN.')
                                player_to_bet.isAllIn = True
                                raise_value = player_to_bet.chips - call_value
                                end_str = '\n%s  ALL IN. '%player_to_bet.player_name
                            bet_count = 1
                            bet_value = raise_value + call_value
                            self.pot.betted_this_round += bet_value
                            player_to_bet.chips += - bet_value
                            player_to_bet.betted_this_round += bet_value
                            self.pot.highestBet += raise_value
                            self.pot.numRaises += 1
                            this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                            this_bet += 'RAISE'
                            this_bet = this_bet.ljust(50)
                            this_bet += 'bet_value = %d chips. '%bet_value
                            this_bet = this_bet.ljust(75)
                            bet_summary += this_bet + end_str
                            if self.pot.numRaises == 3:
                                print('\nRaise limit reached. ')
                        elif action == 'c':
                            bet_value = call_value
                            if call_value >= player_to_bet.chips:
                                print('ALL IN.')
                                player_to_bet.isAllIn = True
                                bet_value = player_to_bet.chips 
                                end_str = '\n%s  ALL IN. '%player_to_bet.player_name                                
                            bet_count += 1
                            self.pot.betted_this_round += bet_value
                            player_to_bet.chips += - bet_value
                            player_to_bet.betted_this_round += bet_value
                            this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                            this_bet += 'CALL'
                            this_bet = this_bet.ljust(50)
                            this_bet += 'bet_value = %d chips. '%bet_value
                            this_bet = this_bet.ljust(75)
                            bet_summary += this_bet + end_str
                        elif action == 'f':
                            bet_count += 1
                            player_to_bet.hasFolded = True
                            if all(player.hasFolded for player in self.players):
                                ## Prevents all players folding on the same hand. 
                                player_to_bet.hasFolded = False
                            else:
                                this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                this_bet += 'FOLD'
                                this_bet = this_bet.ljust(50)
                                this_bet += 'bet_value = %d chips. '%0
                                this_bet = this_bet.ljust(75)
                                bet_summary += this_bet + end_str
                                print('folded')
                    else:
                        if player_to_bet.hasFolded:
                            bet_summary += '\n%s has FOLDED.'%player_to_bet.player_name
                        elif player_to_bet.isAllIn:
                            bet_summary += '\n%s is ALL IN.'%player_to_bet.player_name
                        bet_count += 1
                if (bet_count == self.numPlayers) or (num_players_who_can_bet <= 1):
                    print('\nBetting round completed. ')
                    self.pot.numRaises = 0
                    self.pot.total_value += self.pot.betted_this_round
                    self.pot.betted_this_round = 0
                    self.pot.highestBet = 0
                    for player in self.players:
                        player.betted_this_hand += player.betted_this_round
                        player.betted_this_round = 0
                    break
        
        else:
            while True:
                for i in range(self.pot.smallBlindIndex, self.pot.smallBlindIndex + self.numPlayers):
                    if bet_count == self.numPlayers:
                        break
                    if num_players_who_can_bet <= 1:
                        bet_summary += '%d player remain able to bet. '%num_players_who_can_bet
                        break
                    end_str = ''# formatting
                    ind = i % self.numPlayers
                    player_to_bet = self.players[ind]
                    action = 0# These three initalisations are there
                    bet_value = ' '#so that only valid input is taken from the user (ints for bets and raises)
                    raise_value = ' '# and strings for actions. This ensures typos dont break the code.
                    if self.pot.betted_this_round == 0:
                        if (not player_to_bet.hasFolded) and (not player_to_bet.isAllIn):
                            while action not in ['b', 'c', 'f']:
                                    print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                    action = input('Would you like to BET (b, cost = bet value chips), CHECK (c, cost = 0 chips) or FOLD (f)? ')
                            if action == 'b':
                                while not bet_value.isnumeric():
                                    bet_value = input('Bet how much? (cost = bet value chips) ')
                                bet_value = eval(bet_value)
                                if bet_value >= player_to_bet.chips:
                                    print('ALL IN.')
                                    player_to_bet.isAllIn = True
                                    bet_value = player_to_bet.chips 
                                    end_str = '\n%s  ALL IN. '%player_to_bet.player_name
                                bet_count = 1
                                self.pot.betted_this_round += bet_value
                                player_to_bet.chips += - bet_value
                                player_to_bet.betted_this_round += bet_value
                                self.pot.highestBet += bet_value
                                this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                this_bet += 'BET'
                                this_bet = this_bet.ljust(50)
                                this_bet += 'bet_value = %d chips. '%bet_value
                                this_bet = this_bet.ljust(75)
                                bet_summary += this_bet + end_str
                            elif action == 'c':
                                bet_count += 1
                                this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                this_bet += 'CHECK'
                                this_bet = this_bet.ljust(50)
                                this_bet += 'bet_value = %d chips. '%0
                                this_bet = this_bet.ljust(75)
                                bet_summary += this_bet + end_str
                            elif action == 'f':
                                bet_count += 1
                                player_to_bet.hasFolded = True
                                if all(player.hasFolded for player in self.players):
                                    ## Prevents all players folding on the same hand. 
                                    player_to_bet.hasFolded = False
                                else:
                                    this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                    this_bet += 'FOLD'
                                    this_bet = this_bet.ljust(50)
                                    this_bet += 'bet_value = %d chips. '%0
                                    this_bet = this_bet.ljust(75)
                                    bet_summary += this_bet + end_str
                                    print('folded.')
                        else:
                            if player_to_bet.hasFolded:
                                bet_summary += '\n %s: has FOLDED.'%player_to_bet.player_name
                            elif player_to_bet.isAllIn:
                                bet_summary += '\n %s: is ALL IN.'%player_to_bet.player_name                            
                            bet_count+=1
                    else:
                        if (not player_to_bet.hasFolded) and (not player_to_bet.isAllIn):
                            call_value = self.pot.highestBet - player_to_bet.betted_this_round 
                            if call_value >= player_to_bet.chips:
                                while action not in ['a', 'f']:
                                    print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                    action = input('Would you like to go ALL IN (a, cost = %d chips) or FOLD (f)? '
                                    %player_to_bet.chips)                                    
                            elif self.pot.numRaises < 3: 
                                while action not in ['r', 'c', 'f']:
                                    print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                    action = input('Would you like to RAISE (r, cost = %d + raise value chips), CALL (c, cost = %d chips) or FOLD (f)? '
                                    %(call_value, call_value))
                            else:
                                while action not in ['c', 'f']:
                                    print('\n%s: You have %d chips remaining. '%(player_to_bet.player_name, player_to_bet.chips))
                                    action = input('Would you like to CALL (c, cost = %d chips) or FOLD (f)? '
                                    %(call_value))
                            if action == 'a':
                                bet_value = player_to_bet.chips
                                print('ALL IN.')
                                player_to_bet.isAllIn = True
                                bet_count += 1
                                self.pot.betted_this_round += bet_value
                                player_to_bet.chips += - bet_value
                                player_to_bet.betted_this_round += bet_value
                                this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                this_bet += 'ALL IN'
                                this_bet = this_bet.ljust(50)
                                this_bet += 'bet_value = %d chips. '%bet_value
                                this_bet = this_bet.ljust(75)
                                bet_summary += this_bet + end_str
                            elif action == 'r':
                                while not raise_value.isnumeric():
                                    raise_value = input('Raise by how much? (cost = %d + raise value chips) '%(call_value))
                                raise_value = eval(raise_value)
                                if call_value + raise_value >= player_to_bet.chips:
                                    print('ALL IN.')
                                    player_to_bet.isAllIn = True
                                    raise_value = player_to_bet.chips - call_value
                                    end_str = '\n%s  ALL IN. '%player_to_bet.player_name                                    
                                bet_count = 1
                                bet_value = raise_value + call_value
                                self.pot.betted_this_round += bet_value
                                player_to_bet.chips += - bet_value
                                player_to_bet.betted_this_round += bet_value
                                self.pot.highestBet += raise_value
                                self.pot.numRaises += 1
                                this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                this_bet += 'RAISE'
                                this_bet = this_bet.ljust(50)
                                this_bet += 'bet_value = %d chips. '%bet_value
                                this_bet = this_bet.ljust(75)
                                bet_summary += this_bet + end_str
                                if self.pot.numRaises == 3:
                                    print('\nRaise limit reached. ')
                            elif action == 'c':
                                bet_value = call_value
                                if call_value >= player_to_bet.chips:
                                    print('ALL IN.')
                                    player_to_bet.isAllIn = True
                                    bet_value = player_to_bet.chips 
                                    end_str = '   %s  ALL IN. '%player_to_bet.player_name                                    
                                bet_count += 1
                                self.pot.betted_this_round += bet_value
                                player_to_bet.chips += - bet_value
                                player_to_bet.betted_this_round += bet_value
                                this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                this_bet += 'CALL'
                                this_bet = this_bet.ljust(50)
                                this_bet += 'bet_value = %d chips. '%bet_value
                                this_bet = this_bet.ljust(75)
                                bet_summary += this_bet + end_str
                            elif action == 'f':
                                bet_count += 1
                                player_to_bet.hasFolded = True
                                if all(player.hasFolded for player in self.players):
                                    ## Prevents all players folding on the same hand. 
                                    player_to_bet.hasFolded = False
                                else:
                                    this_bet = '\n%s'%player_to_bet.player_name.ljust(25)
                                    this_bet += 'FOLD'
                                    this_bet = this_bet.ljust(50)
                                    this_bet += 'bet_value = %d chips. '%0
                                    this_bet = this_bet.ljust(75)
                                    bet_summary += this_bet + end_str
                                    print('folded')
                        else:
                            if player_to_bet.hasFolded:
                                bet_summary += '\n%s has FOLDED.'%player_to_bet.player_name
                            elif player_to_bet.isAllIn:
                                bet_summary += '\n%s is ALL IN.'%player_to_bet.player_name                            
                            bet_count += 1
                if (bet_count == self.numPlayers) or (num_players_who_can_bet <= 1):
                    print('\nBetting round completed. ')
                    self.pot.numRaises = 0
                    self.pot.total_value += self.pot.betted_this_round
                    self.pot.betted_this_round = 0
                    self.pot.highestBet = 0
                    for player in self.players:
                        player.betted_this_hand += player.betted_this_round
                        player.betted_this_round = 0
                    break                        
                    
        return bet_summary
        #End. 

    def showdown(self, flop, turn, river):
        ''' Decides which players (of those still in after the river) win and how many chips they gain.
            Correctly deals with side pots (which result iff players are ALL IN.)
         '''
        print('\n')
        folded_players = [player.hasFolded for player in self.players]
        if not any(folded_players):
            players_in_showdown = self.players
        else: 
            players_in_showdown = [player for player in self.players if not player.hasFolded]
        
        all_in_players = [player.isAllIn for player in players_in_showdown]
        
        for player in self.players:
            possible_cards = player.hole_cards + flop + turn + river
            player.get_best_hand(possible_cards)
            best_hand = player.best_hand
            if not player.hasFolded:
                print("\n %s's best hand is type: %s with score %d"%(player.player_name, best_hand[2], best_hand[1]))
                print([str(card) for card in best_hand[0]]) 
                print('\n')
            else:
                print("\n%s FOLDED. "%player.player_name)
        
        showdown_summary = '\n=====================================\n'
        showdown_summary += '\n\nMore detailed showdown summary: \n'
        amount_players_betted = [player.betted_this_hand for player in players_in_showdown]
        nPots = len(list(set(amount_players_betted)))## Number of unique values in the list 'amount_players_betted'. 
        showdown_summary += '\nNumber of active pots:   %d'%nPots
        showdown_summary += '\nTotal pot size = %d chips\n'%self.pot.total_value
        showdown_summary += '\n=====================================\n'            
        showdown_summary += 'Communal cards: \n'
        showdown_summary += '\nFlop:\n'
        for card in flop:
            showdown_summary += ''.ljust(10) + str(card) + '\n'
        showdown_summary += '\nTurn:\n'
        for card in turn:
            showdown_summary += ''.ljust(10) + str(card) + '\n'
        showdown_summary += '\nRiver:\n'
        for card in river:
            showdown_summary += ''.ljust(10) + str(card) + '\n'            
        
        for player in self.players:
            showdown_summary += '\n=====================================\n'
            showdown_summary += '\n%s hand: \n'%player.player_name
            showdown_summary += '\nHOLE CARDS: \n'
            for card in player.hole_cards:
                if player.hasFolded:
                    showdown_summary += '\n'.ljust(10) + 'FOLDED. '
                else:
                    showdown_summary += '\n'.ljust(10) + '%s'%str(card)
            
            showdown_summary += '\n\nBEST HAND: \n'                
            for card in player.best_hand[0]:
                if player.hasFolded:
                    showdown_summary += '\n'.ljust(10) + 'FOLDED. '
                else:
                    showdown_summary += '\n'.ljust(10) + '%s'%str(card)
            
            if not player.hasFolded:
                showdown_summary += ('\n\nBest hand type: %s'%player.best_hand[2]).ljust(35) + ('score: %s\n'%player.best_hand[1]).ljust(35)
            
        showdown_summary += '\n=====================================\n'
        
        if not any(all_in_players):
            ### Standard show down -- no side pots.             
            hand_scores=[]
            for player in players_in_showdown:
                hand_scores.append(player.best_hand[1])                    
            max_score = max(hand_scores)
            winning_players = [player for ind, player in enumerate(players_in_showdown) if hand_scores[ind] == max_score]
            if len(winning_players) == 1:
                ### Only one winner. 
                winning_score = max_score
                winning_player = winning_players[0]#players_in_showdown[hand_scores.index(winning_score)]
                print('\n\nWinning player is %s, with hand: %s, of type: %s \n\n'
                %(winning_player.player_name, [str(card) for card in winning_player.best_hand[0]], winning_player.best_hand[2]))
                print('\n%s wins %d chips'
                %(winning_player.player_name, self.pot.total_value))
                winning_player.chips += self.pot.total_value
                
                for player in self.players[::-1]:                    
                    showdown_summary = '\n%s has %d chips remaining. '%(player.player_name, player.chips) + showdown_summary
                
                showdown_summary = '\n%s wins %d chips\n\n'%(
                winning_player.player_name, self.pot.total_value) + showdown_summary
                
                showdown_summary = '\n\nWinning player is %s,\n with hand: %s,\n of type: %s \n'%(
                winning_player.player_name, ', '.join([str(card) for card in winning_player.best_hand[0]]), winning_player.best_hand[2]) + showdown_summary
                                            
            else:
                ### Multiple hands with same score.
                print('\nTie for winning hand!')
                numWinners = len(winning_players)
                winnings = [0 for ind in range(numWinners)]
                for ind in range(1,numWinners):
                    winnings[ind] = self.pot.total_value // numWinners## Floor division
                winnings[0] = self.pot.total_value - sum(winnings)## Player closest to dealer gets any remainder. 
                for index, player in enumerate(self.players):
                    if player.isDealer:
                        break
                win_count = 0
                for i in range(index, index + self.numPlayers):
                    ind = i % self.numPlayers
                    if self.players[ind] in winning_players:
                        winning_player = self.players[ind]
                        print('\nTied player number %d is %s,\n with hand: %s,\n of type: %s \n'
                        %(win_count+1, winning_player.player_name, [str(card) for card in winning_player.best_hand[0]], winning_player.best_hand[2]))
                        print('\n%s wins %d chips'
                        %(winning_player.player_name, winnings[win_count]))
                        winning_player.chips += winnings[win_count]
                        win_count += 1
                        
                for player in self.players[::-1]:                    
                    showdown_summary = '\n%s has %d chips remaining. '%(player.player_name, player.chips) + showdown_summary
                
                win_count = 0                
                for i in range(index, index + self.numPlayers):
                    ind = i % self.numPlayers
                    if self.players[ind] in winning_players:
                        winning_player = self.players[ind]
                        
                        showdown_summary = '\n%s wins %d chips\n'%(
                        winning_player.player_name, winnings[win_count]) + showdown_summary
                
                        showdown_summary = '\n Tie for winning hand! \n\nWinning player %d is %s,\n with hand: %s,\n of type: %s \n'%(len(winnings)-win_count, 
                        winning_player.player_name, ', '.join([str(card) for card in winning_player.best_hand[0]]), winning_player.best_hand[2]) + showdown_summary
                        win_count += 1
                        
            for player in self.players:
                print('\n%s has %d chips remaining. '
                %(player.player_name, player.chips))
                     
        else:
            ## We have side-pots, this results from some players being 'All In' and likely not having bet 
            ## the same amount to get to the showdown.
            amount_players_betted = [player.betted_this_hand for player in players_in_showdown]
            ## Players who have folded may still have betted
            other_bets = [player.betted_this_hand if player not in players_in_showdown else 0 for player in self.players]
            
            nPots = len(list(set(amount_players_betted)))## Number of unique values in the list 'amount_players_betted'. 
            print(nPots)
            i = 1
            players_in_pot = players_in_showdown
            
            pot_sum = '\n=====================================\n'
            pot_sum += '\nPot %d summary:  '%i                        
            while len(players_in_pot) >= 1:### Breaks when all pots have been sorted.
                if i!=1:
                    pot_sum += '\n=====================================\n'
                    pot_sum += '\nPot %d summary:  '%i
                print([player.player_name for player in players_in_pot])
                print(*amount_players_betted)
                pot_sum += '\nPlayers involved:   %s'%',  '.join([player.player_name for player in players_in_pot])
                potVal = len(players_in_pot) * min(amount_players_betted)
                eachPlayerBetted = min(amount_players_betted)
                for ind, betVal in enumerate(other_bets):
                    potVal += min(betVal, eachPlayerBetted)
                    other_bets[ind] = max(0, betVal-eachPlayerBetted)
                
                print('Pot %d value = %d'%(i, potVal))
                
                pot_sum += '\nPot Value = %d chips.'%potVal
                
                hand_scores=[]
                for player in players_in_pot:
                    hand_scores.append(player.best_hand[1])
                
                max_score = max(hand_scores)
                winning_players = [player for ind, player in enumerate(players_in_pot) if hand_scores[ind] == max_score]
                if len(winning_players) == 1:
                    ### Only one winner. 
                    winning_score = max_score
                    winning_player = players_in_pot[hand_scores.index(winning_score)]
                    print('\nWinning player is %s, with hand: %s, of type: %s \n'
                    %(winning_player.player_name, [str(card) for card in winning_player.best_hand[0]], winning_player.best_hand[2]))
                    print('\n%s wins %d chips'
                    %(winning_player.player_name, potVal))
                    winning_player.chips += potVal
                    pot_sum += '\n\nWinning player is %s,\n with hand: %s,\n of type: %s \n'%(
                    winning_player.player_name, ', '.join([str(card) for card in winning_player.best_hand[0]]), winning_player.best_hand[2])                    
                    pot_sum += '\n%s wins %d chips\n\n'%(winning_player.player_name, potVal)
                else:
                    ### Multiple winners.  
                    print('\nTie for winning hand!')
                    numWinners = len(winning_players)
                    winnings = [0 for ind in range(numWinners)]
                    for ind in range(1,numWinners):
                        winnings[ind] = potVal // numWinners## Floor division
                    winnings[0] = potVal - sum(winnings)## Player closest to dealer gets any remainder. 
                    for index, player in enumerate(self.players):
                        if player.isDealer:
                            break
                    win_count = 0
                    for i in range(index, index + self.numPlayers):
                        ind = i % self.numPlayers
                        if self.players[ind] in winning_players:
                            winning_player = self.players[ind]
                            print('\nTied player number %d is %s,\n with hand: %s,\n of type: %s \n'
                            %(win_count+1, winning_player.player_name, [str(card) for card in winning_player.best_hand[0]], winning_player.best_hand[2]))
                            print('\n%s wins %d chips'
                            %(winning_player.player_name, winnings[win_count]))
                            winning_player.chips += winnings[win_count]
                            win_count += 1
                    
                    win_count = 0                
                    for i in range(index, index + self.numPlayers):
                        ind = i % self.numPlayers
                        if self.players[ind] in winning_players:
                            winning_player = self.players[ind]  
                            pot_sum += '\n Tie for winning hand! \n\nWinning player %d is %s,\n with hand: %s,\n of type: %s \n'%(win_count+1, 
                            winning_player.player_name, ', '.join([str(card) for card in winning_player.best_hand[0]]),
                             winning_player.best_hand[2])                                                  
                            pot_sum += '\n%s wins %d chips\n'%(
                            winning_player.player_name, winnings[win_count])
                                                        
                            win_count += 1
                    
                    
                
                next_pot_players = []
                next_pot_player_bets = []
                
                for index, player in enumerate(players_in_pot):
                    amount_players_betted[index] += - eachPlayerBetted
                    if not amount_players_betted[index] == 0:
                        next_pot_players.append(player)
                        next_pot_player_bets.append(amount_players_betted[index])
                        
                players_in_pot = next_pot_players
                amount_players_betted = next_pot_player_bets
                i+=1
            
            
            for player in self.players[::-1]:                    
                showdown_summary = '\n%s has %d chips remaining. '%(player.player_name, player.chips) + showdown_summary
            
            pot_sum += '\n=====================================\n'
            showdown_summary = pot_sum + showdown_summary
            print(pot_sum)
            
            for player in self.players:
                print('\n%s has %d chips remaining. '
                %(player.player_name, player.chips))
            
        
        com_card_sum = '\nCommunal cards: \n'
        com_card_sum += '\nFlop:'
        for ind, card in enumerate(flop):
            if ind == 0:
                com_card_sum += ''.ljust(10) + str(card) + '\n'
            else:
                com_card_sum += ''.ljust(15) + str(card) + '\n'
        com_card_sum += 'Turn:'
        for card in turn:
            com_card_sum += ''.ljust(10) + str(card) + '\n'
        com_card_sum += 'River:'
        for card in river:
            com_card_sum += ''.ljust(9) + str(card) + '\n'            
        
        showdown_summary = com_card_sum + showdown_summary
        
        for player in self.players[::-1]:
            card_summary = ("%s's hole cards: "%player.player_name).ljust(25) 
            for ind, card in enumerate(player.hole_cards):
                if player.hasFolded:
                    card_summary += 'FOLDED' 
                    card_summary = card_summary.ljust(50 + ind*25)
                else:
                    card_summary += '%s'%str(card) 
                    card_summary = card_summary.ljust(50 + ind*25)
                                                
            showdown_summary = card_summary + '\n' + showdown_summary
        showdown_summary = 'RESULTS: \n\n' + showdown_summary
        
        return showdown_summary        
        
    def configure_dropbox_folders(self):
        ''' Makes a bunch of dropbox folders. 
            If they dont already exist. '''
        for player in self.players:
            if not os.path.isdir(Dropbox_file_root):
                os.mkdir(Dropbox_file_root)
                os.mkdir(Dropbox_file_root+player.player_name)
            elif not os.path.isdir(Dropbox_file_root + player.player_name):
                os.mkdir(Dropbox_file_root+player.player_name)
        return None
        
    def dropbox_start_up(self):
        for player1 in self.players:            
            message = """Welcome %s to
    
            %s
    
            You will be playing:  %s
            with: %s 

            You are playing for:   %d chips
            """%(player1.player_name, branding, 
            self.game_type, ',  '.join([player.player_name for player in self.players if player is not player1])
            , sum([player.chips for player in self.players]))
            with open(Dropbox_file_root+player1.player_name+'/STARTUP'+'.txt', 'w+') as test_file:
                test_file.write(message)
        
        for player in self.players:
            if not os.path.isfile(Dropbox_file_root+player.player_name+'/CONTRACT'+'.txt'):
                contract = f"""{branding} 
            
                I, {player.player_name}, hereby agree to the rules of Mummrehs Casino Texas Holdem: 
                """
                contract += '\n' + contract_main_body
                contract += contract_money_rules
                contract += """
                
                Signed:"""
                            
                with open(Dropbox_file_root+player.player_name+'/CONTRACT'+'.txt', 'w+') as test_file:
                    test_file.write(contract)
            
        return None

            
    def dropbox_update(self, flop=[' ',' ',' '], turn=[' '], river=[' '], bet_summaries=['']):
        if str(flop[0]) == ' ':
            pot_val = 0
        else:
            pot_val = self.pot.total_value
                    
        message = """Card update. 

            Game type:  %s
            Hand number:  %s
            Players in game: %s 
            Players in hand: %s 
    
            Small blind: %d chips
            Big blind:   %d chips  

            Pot Value:   %d chips
        """%(
        self.game_type, self.numHand, ',  '.join([player.player_name for player in self.players])
        , ',  '.join([player.player_name for player in self.players if not player.hasFolded]), self.smallBlindValue, self.bigBlindValue, pot_val)
        message += '\nPlayer stats:\n\n'
    
        for dealerIndex, player in enumerate(self.players):
            if player.isDealer:
                break
        
        smallBlindIndex = (dealerIndex+1) % self.numPlayers
        bigBlindIndex = (dealerIndex+2) % self.numPlayers
    
        messages = []
        player_you_messages = []
        player_not_you_messages = []
        blank_card = '##################'
    
        for i, player1 in enumerate(self.players):
            player_message = ''
            other_player_message = ''
            P1blindStatus = 'None'
            if i == dealerIndex:
                P1blindStatus = 'Dealer'
            if i == smallBlindIndex:
                P1blindStatus = 'Small Blind'
            if i == bigBlindIndex:
                P1blindStatus = 'Big Blind'
            for j, player2 in enumerate(self.players):
                P2blindStatus = 'None'
                if j == dealerIndex:
                    P2blindStatus = 'Dealer'
                if j == smallBlindIndex:
                    P2blindStatus = 'Small Blind'
                if j == bigBlindIndex:
                    P2blindStatus = 'Big Blind'                
                if player1 == player2:
                    stats_line =  "*******************************************\n"
                    stats_line += ("*       Player name:    %s"%player1.player_name).ljust(42)+'*' +'   Flop:     %s\n'%str(flop[0])
                    stats_line += ("*       Chips remaining:    %s"%player1.chips).ljust(42)+'*'   +'             %s\n'%str(flop[1])
                    stats_line += ("*       Chips betted this hand:    %s"%player1.betted_this_hand).ljust(42)+'*' +'             %s\n'%str(flop[2])
                    stats_line += '*'.ljust(42)+'*\n'
                    stats_line += ("*       Card 1:    %s"%player1.hole_cards[0]).ljust(42)+'*\n'
                    stats_line += ("*       Card 2:    %s"%player1.hole_cards[1]).ljust(42)+'*' +'   Turn:     %s\n'%str(turn[0])
                    stats_line += '*'.ljust(42)+'*\n'
                    stats_line += ("*       Folded:    %s"%player1.hasFolded).ljust(42)+'*\n'     
                    stats_line += ("*       Blinds:    %s"%P1blindStatus).ljust(42)+ '*' +'   River:    %s\n'%str(river[0])
                    stats_line += "*******************************************"   
                    player_message += stats_line + '\n\n'
                else:
                    stats_line  = "        Player name:    %s\n"%player2.player_name
                    stats_line += "        Chips remaining:    %s\n"%player2.chips
                    stats_line += "        Chips betted this hand:    %s\n"%player2.betted_this_hand
                    stats_line += "        Card 1:    %s\n"%blank_card
                    stats_line += "        Card 2:    %s\n"%blank_card
                    stats_line += "        Folded:    %s\n"%player2.hasFolded
                    stats_line += "        Blinds:    %s\n"%P2blindStatus
                    other_player_message += stats_line + '\n\n'
        
            if bet_summaries[0] == '':
                message_total = message+player_message+'\nOther players: \n\n'+other_player_message+'\n\n\n\n End.'
                messages.append(message_total)    
            else:
                message_total = message+player_message
                for j, bet_summary in enumerate(bet_summaries[::-1]):
                    message_total += 'Betting round %d: '%(len(bet_summaries)-j) + bet_summary.replace('Betting round summary:','') +'\n\n'
                message_total += '\n\n\nOther players: \n\n'+other_player_message+'\n\n\n\n End.'
                messages.append(message_total)
    
        for i, player in enumerate(self.players): 
            with open(Dropbox_file_root+player.player_name+'/UPDATE'+'.txt', 'w+') as test_file:
                test_file.write(branding)
                test_file.write(messages[i])
            
    
    def dropbox_showdown_summary(self, showdown_summary, bet_summaries):        
        for j, bet_summary in enumerate(bet_summaries[::-1]):
            showdown_summary += 'Betting round %d: '%(len(bet_summaries)-j) + bet_summary.replace('Betting round summary:','') +'\n\n'        
        for player in self.players: 
            with open(Dropbox_file_root+player.player_name+'/UPDATE'+'.txt', 'w+') as test_file:
                test_file.write(branding)
                test_file.write(showdown_summary + '\n\n\n\n End.')
        return None
    
    def dropbox_update_game_log(self, flop, turn, river):
        message = '\n================================================================================================\n'
        message += '\n Game summary at end of hand %d\n'%self.numHand
        for player in self.players:
            message += '\n%s has %d chips remaining. '%(player.player_name, player.chips)
        message += '\n\n'
        for player in self.players:
            card_summary = ("%s's hole cards: "%player.player_name).ljust(25) 
            for ind, card in enumerate(player.hole_cards):
                if player.hasFolded:
                    card_summary += 'FOLDED' 
                    card_summary = card_summary.ljust(50 + ind*25)
                else:
                    card_summary += '%s'%str(card) 
                    card_summary = card_summary.ljust(50 + ind*25)
        
            message += card_summary+'\n'    
        
        com_card_sum = '\nFlop:'
        for ind, card in enumerate(flop):
            if ind == 0:
                com_card_sum += ''.ljust(10) + str(card) + '\n'
            else:
                com_card_sum += ''.ljust(15) + str(card) + '\n'
        com_card_sum += 'Turn:'
        for card in turn:
            com_card_sum += ''.ljust(10) + str(card) + '\n'
        com_card_sum += 'River:'
        for card in river:
            com_card_sum += ''.ljust(9) + str(card) + '\n'            
        message += com_card_sum    
        
        for player in self.players: 
            with open(Dropbox_file_root+player.player_name+'/GAMELOG'+'.txt', 'a') as test_file:#a for append.
                test_file.write(message)
        
        
        return None
        
    def configure_dealer_email(self):
        port = 465
        smtp_server = "smtp.gmail.com"

        dealer_email = input('Input email address of the account which will act as the dealer: ')
        if dealer_email[-10:] != '@gmail.com':
            raise ValueError('TexasHoldEm email only configured for gmail. You have input the non-gmail account: %s'%dealer_email)
    
        self.dealer_email = dealer_email   
        dealer_password = getpass.getpass(prompt='Email password: ', stream=None)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
            try:
                server.login(dealer_email,dealer_password)
                self.dealer_password = dealer_password
            except smtplib.SMTPAuthenticationError:
                print('Cannot log in. (Check password is correct and that permission for less secure apps is turned ON.)')
                self.dealer_password = None                
        return None

    def send_start_up_email(self):
        port = 465
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()
        sender_email = self.dealer_email
        sender_email_password = self.dealer_password
    
        for player1 in self.players:
            print(player1.player_name)
        
            message = """Welcome %s to
    
            %s
    
            You will be playing:  %s
            with: %s 

            You are playing for:   %d chips
            """%(player1.player_name, branding, 
            self.game_type, ',  '.join([player.player_name for player in self.players if player is not player1])
            , sum([player.chips for player in self.players]))
        
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Welcome to ' + self.game_name
            msg['From'] = sender_email
    
            with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
                server.login(sender_email, sender_email_password)        
                reciever_email = player1.player_email
                msg['To'] = reciever_email
                html = """\
                <html>
                  <head>
                  <style>
                      p4 {
                          color: black;
                          text-align: left;
                          font-size: 10px;
                          font-family: monospace;
                          white-space: pre;                          
                         }
                  </style>
                  </head>
                  <body>
                  <p4>%s<\p4>
                  </body>
                </html>
                """%message.replace('\n', '<br>').replace(' ',' ')
                email_text = MIMEText(html, 'html')
                msg.attach(email_text)
                server.sendmail(sender_email,reciever_email,msg.as_string())
                print('\n%s emailed. '%player1.player_name)
            
        return None                            
    
    
    def email_card_update(self, flop=[' ', ' ', ' '], turn=[' '], river=[' ']):
        if str(flop[0]) == ' ':
            pot_val = 0
        else:
            pot_val = self.pot.total_value
    
        message = """Card update. 

            Game type:  %s
            Hand number:  %s
            Players in game: %s 
            Players in hand: %s 
    
            Small blind: %d chips
            Big blind:   %d chips  

            Pot Value:   %d chips
        """%(
        self.game_type, self.numHand, ',  '.join([player.player_name for player in self.players])
        , ',  '.join([player.player_name for player in self.players if not player.hasFolded]), self.smallBlindValue, self.bigBlindValue, pot_val)
    
        message += '\nPlayer stats:\n\n'
        blank_card = '##################'
        messages = []
    
        for dealerIndex, player in enumerate(self.players):
            if player.isDealer:
                break
        smallBlindIndex = (dealerIndex+1) % self.numPlayers
        bigBlindIndex = (dealerIndex+2) % self.numPlayers
    
    
        for i, player1 in enumerate(self.players):
            player_message = message
            P1blindStatus = 'None'
            if i == dealerIndex:
                P1blindStatus = 'Dealer'
            if i == smallBlindIndex:
                P1blindStatus = 'Small Blind'
            if i == bigBlindIndex:
                P1blindStatus = 'Big Blind'
            for j, player2 in enumerate(self.players):
                P2blindStatus = 'None'
                if j == dealerIndex:
                    P2blindStatus = 'Dealer'
                if j == smallBlindIndex:
                    P2blindStatus = 'Small Blind'
                if j == bigBlindIndex:
                    P2blindStatus = 'Big Blind'                
                if player1 == player2:
                    stats_line =  "*******************************************\n"
                    stats_line += ("*       Player name:    %s"%player1.player_name).ljust(42)+'*' +'   Flop:     %s\n'%str(flop[0])
                    stats_line += ("*       Chips remaining:    %s"%player1.chips).ljust(42)+'*'   +'             %s\n'%str(flop[1])
                    stats_line += ("*       Chips betted this hand:    %s"%player1.betted_this_hand).ljust(42)+'*' +'             %s\n'%str(flop[2])
                    stats_line += '*'.ljust(42)+'*\n'
                    stats_line += ("*       Card 1:    %s"%player1.hole_cards[0]).ljust(42)+'*\n'
                    stats_line += ("*       Card 2:    %s"%player1.hole_cards[1]).ljust(42)+'*' +'   Turn:     %s\n'%str(turn[0])
                    stats_line += '*'.ljust(42)+'*\n'
                    stats_line += ("*       Folded:    %s"%player1.hasFolded).ljust(42)+'*\n'     
                    stats_line += ("*       Blinds:    %s"%P1blindStatus).ljust(42)+ '*' +'   River:    %s\n'%str(river[0])
                    stats_line += "*******************************************"   
                else:
                    stats_line  = "        Player name:    %s\n"%player2.player_name
                    stats_line += "        Chips remaining:    %s\n"%player2.chips
                    stats_line += "        Chips betted this hand:    %s\n"%player2.betted_this_hand
                    stats_line += "        Card 1:    %s\n"%blank_card
                    stats_line += "        Card 2:    %s\n"%blank_card
                    stats_line += "        Folded:    %s\n"%player2.hasFolded
                    stats_line += "        Blinds:    %s\n"%P2blindStatus
                
            
                player_message += stats_line
                player_message += '\n\n'
            messages.append(player_message)    
                    
    
        port = 465
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()
        sender_email = self.dealer_email
        sender_email_password = self.dealer_password
    
        with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
            server.login(sender_email, sender_email_password)        
            for ind, player in enumerate(self.players):
                msg = MIMEMultipart('alternative')
                msg['Subject'] = self.game_name
                msg['From'] = sender_email                                
                reciever_email = player.player_email
                msg['To'] = reciever_email
                html = """\
                <html>
                  <head>
                  <style>
                      p4 {
                          color: black;
                          text-align: left;
                          font-size: 12px;
                          font-family: monospace;
                          white-space: pre;                          
                         }
                  </style>
                  </head>
                  <body>
                  <p4>%s</p4>
                  </body>
                </html>
                """%messages[ind].replace('\n', '<br>').replace(' ',' ')
                email_text = MIMEText(html, 'html')
                msg.attach(email_text)
                server.sendmail(sender_email,reciever_email,msg.as_string())
                print('\n%s emailed. '%player.player_name)
            
        return None

    def email_bet_summary(self, bet_summary):
        port = 465
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()
        sender_email = self.dealer_email
        sender_email_password = self.dealer_password
            
        with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
            server.login(sender_email, sender_email_password)        
            for player in self.players:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = self.game_name
                msg['From'] = sender_email                
                reciever_email = player.player_email
                msg['To'] = reciever_email
                html = """\
                <html>
                  <head>
                  <style>
                      p4 {
                          color: black;
                          text-align: left;
                          font-size: 12px;
                          font-family: monospace;
                          white-space: pre;                          
                         }
                  </style>
                  </head>
                  <body>
                  <p4>%s</p4>
                  </body>
                </html>
                """%bet_summary.replace('\n', '<br>').replace(' ',' ')
                email_text = MIMEText(html, 'html')
                msg.attach(email_text)
                server.sendmail(sender_email,reciever_email,msg.as_string())
                print('\n%s emailed. '%player.player_name)
    
    def email_showdown_summary(self, showdown_summary):
        port = 465
        smtp_server = "smtp.gmail.com"
        context = ssl.create_default_context()
        sender_email = self.dealer_email
        sender_email_password = self.dealer_password
            
        with smtplib.SMTP_SSL(smtp_server,port,context=context) as server:
            server.login(sender_email, sender_email_password)        
            for player in self.players:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = self.game_name
                msg['From'] = sender_email                
                reciever_email = player.player_email
                msg['To'] = reciever_email
                html = """\
                <html>
                  <head>
                  <style>
                      p4 {
                          color: black;
                          text-align: left;
                          font-size: 12px;
                          font-family: monospace;
                          white-space: pre;                          
                         }
                  </style>
                  </head>
                  <body>
                  <p4>%s</p4>
                  </body>
                </html>
                """%showdown_summary.replace('\n', '<br>').replace(' ',' ')
                email_text = MIMEText(html, 'html')
                msg.attach(email_text)
                server.sendmail(sender_email,reciever_email,msg.as_string())
                print('\n%s emailed. '%player.player_name)
    
        return None
        
        
        # End. 
        



if __name__ == "__main__":
    LetsPlayCards()
    



# END.
