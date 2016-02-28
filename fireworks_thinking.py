#!/opt/local/bin/python


visible_cards_in_hands = []
visible_cards_in_discard_deck = []
top_cards_on_board = []
player_hand_knowledge = []


# Start
# Figure out who's turn it is
q = 'MATCH (t:Token {name: "Player_Turn" }), (p:Player) WHERE (t)-[:IS]->(p) RETURN p.name'
results = db.query(q, returns=(str))
active_player_name = results[0][0]

################ LOOK AT ALL POSSIBLE ATTAINABLE INFORMATION ################
# He looks at all the player's cards
q = 'MATCH (p:Player {name: "' + active_player_name +'" }), (c:Card) WHERE (p)-[:CAN_SEE]->(c) RETURN c.value, c.position, c.color, p.name'
results = db.query(q, returns=(int, int, str, str))
for r in results:
    visible_cards_in_hands.extend([r[0],r[1],r[2],r[3]])

# He looks at what's been discarded
q = 'MATCH (d:Deck {name: "Discard_Deck" }), (c:Card) WHERE (d)-[:CONTAINS]->(c) RETURN c.value, c.color'
results = db.query(q, returns=(str))
for r in results:
    visible_cards_in_discard_deck.extend([r[0],r[1]])
    
# He looks at the game board
q = 'MATCH (c:Card {c.column_order: "Top") RETURN c.value, c.color'
results = db.query(q, returns=(str))
for r in results:
    top_cards_on_board.extend([r[0],r[1]])

# He thinks about the cards he has
q = 'MATCH (p:Player {name: "' + active_player_name +'" }), (ci:Card) WHERE (p)-[:KNOWS]->(ci) RETURN ci.value, ci.color, ci.name'
results = db.query(q, returns=(int, int, str, str))
for r in results:
    player_hand_knowledge.extend([r[0],r[1],r[2]])
  
# See how many Info Tokens are available
q = 'MATCH (t:Token {type: "Info", }) WHERE t.used == False RETURN t.name'
results = db.query(q, returns=(str))
active_player_name = results[0][0]

################ THE PLAYER THINKS !!!!! ################

# Actions: 1) Gives information, 2) plays card

weight_give_info = 0
weight_play_card = 0

################ ASSESS THE NEED OF ALL THE OTHER CARDS TO BE PLAYED !!!!! ################

if strategy_look_at_card_hand_order == 1:
    # Check the thing out ... 
    # 
    # 
    # 


# He crunches through a couple of agreed to philosophies
# {Expanse of effort} 
# He decides to throw a card away, put a card down, or to give advice
# He organizes his/her own card order if he/she picked up a card

# Next player Go & Repeat

# Game is done when either 1) there is one more round after draw deck = 0, 2) all the columns are done, or 3) there are 3 failures to put down.


# Strategies: 
# Only observe X players
# Information means playable or don't play
# Complete knowledge first, before playing
# A player never gives info for a dead color
# A player can give info for a dead color if he should not throw out the next couple of cards.