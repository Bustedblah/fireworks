#!/opt/local/bin/python
#
#

#####################################################################
# Import Modules
#####################################################################

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
from oct2py import octave
from hanabi_classes import hanabi_card  # NOTE: Not sure if i need to do this.
from hanabi_classes import hanabi_deck

###############################################################
# DEFINE FUNCTION: 
###############################################################


################## ADD TOP CARD TO THE HAND ###################
def add_top_card_to_a_hand(name_of_the_hand,total_num_cards):

    # Find the name and order # of the top card
    q = 'MATCH (c:Card) WHERE (:Token { name:"Top_Card" })-[:IS]->(c) RETURN c.name, c.order'
    results_c_order = db.query(q, returns=(str, int))
    print results_c_order[0]
    
    if results_c_order != []:
        name_of_old_top_card = results_c_order[0][0]
        order_of_top_card = results_c_order[0][1]
        
        if order_of_top_card < total_num_cards:
            # Make the next card the top card
            q = 'MATCH (t:Token {name:"Top_Card"}), (c:Card {order:' + str(order_of_top_card+1) + '}) CREATE (t)-[:IS]->(c)'
            results_blank = db.query(q)
    
        # Remove the old top card from being the top card
        q = 'START t=node(*) MATCH t-[rel:IS]->c WHERE t.name="Top_Card" AND c.name="' + name_of_old_top_card + '" DELETE rel'
        results_blank = db.query(q)
        # Remove the old top card from the deck
        q = 'START d=node(*) MATCH d-[rel:CONTAINS]->c WHERE d.name = "Draw_Deck" AND c.name= "' + name_of_old_top_card + '" DELETE rel'
        results_blank = db.query(q)

        # Add that card to the present hand
        q = 'MATCH (h:Hand {name: "' + name_of_the_hand + '" }), (c:Card {name: "' + name_of_old_top_card + '" }) CREATE (h)-[:CONTAINS]->(c)'
        results_blank = db.query(q)
         
################## SEE IF THERE ARE LESS THAN X NUMBER OF CARDS IN THE HANDS ###################
def check_num_cards_per_hand(cards_per_hand):
    done = 1
    q = 'MATCH (h:Hand) RETURN h.name'
    results_3 = db.query(q, returns=(str))
    for r in results_3:
        name_of_the_hand = r[0]
        print r[0]
        q = 'MATCH (h:Hand {name: "' + name_of_the_hand + '" }), (c:Card) WHERE (h)-[:CONTAINS]->(c) RETURN count(*)'
        results_4 = db.query(q, returns=(int))
        if results_4[0][0] != cards_per_hand:
            done = 0
    return done    
        

#####################################################################
# Initialize Game Constants
#####################################################################

# TODO: MAKE THIS AN INPUT IN SOME FASHION
# Number of Game Players
num_players = 4
# Default card structure for the game
default_card_struct = [3,2,2,2,1]
# Number of colors in play
num_colors_in_play = 5
# Number of info_tokens
num_info_tokens = 10
# Number of wrong answer tokens
num_wrong_answer_tokens = 3
    
if num_players == 4 or 5:
    cards_per_hand = 4
elif num_players == 2 or 3:
    cards_per_hand = 5
else:
    cards_per_hand = 0
    # TODO: Break out of this loop and Error

total_num_cards = 0
for num in default_card_struct:
    total_num_cards = total_num_cards + num*num_colors_in_play

#####################################################################
# Initialize Node Type and Clean the Database
#####################################################################

db = GraphDatabase("http://localhost:7474", username="neo4j", password="mypassword")
 
q1 = 'START n = node(*) OPTIONAL MATCH n-[r]-() WHERE (ID(n)>0 AND ID(n)<10000) DELETE n, r'
results = db.query(q1) 

# TODO: Set this up with a running check to ensure that all the pre-existing data has
#       been removed.

player = db.labels.create("Player")
hand = db.labels.create("Hand")
card = db.labels.create("Card")
token = db.labels.create("Token")
deck = db.labels.create("Deck")

players_list_names = {}
players_list_nodes = {}
hand_list_names = {}
hand_list_nodes = {}
card_list_names = {}
card_list_nodes = {}
info_token_list_names = {}
info_token_list_nodes = {}
w_answer_token_list_names = {}
w_answer_token_list_nodes = {}

p_name = 'blank'
p_node_name = 'p0'
h_name = 'blank'
h_node_name = 'h0'
c_name = 'blank'
c_node_name = 'c0'
dr_d_name = 'blank'
dr_d_node_name = 'dr_d0'
dis_d_name = 'blank'
dis_d_node_name = 'dis_d0'
i_name = 'blank'
i_node_name = 'i0'
wa_name = 'blank'
wa_node_name = 'wa0'

#####################################################################
# SET-UP PLAYERS AND THEIR (BLANK) HANDS
#####################################################################

k = 0
while k < num_players:
    key = k
    p_name = "Player_" + str(key+1)
    p_node_name = "p" + str(key+1)
    players_list_names[key] = p_name 
    players_list_nodes[key] = p_node_name
    p_node_name = db.nodes.create(name=p_name)
    player.add(p_node_name)
    
    h_name = "Hand_" + str(key+1)
    h_node_name = "h" + str(key+1)
    hand_list_names[key] = h_name 
    hand_list_nodes[key] = h_node_name
    h_node_name = db.nodes.create(name=h_name)
    hand.add(h_node_name)
    
    p_node_name.relationships.create("CONTROLS", h_node_name)
    
    k += 1
        
#####################################################################
# SET-UP GAME PIECES
#####################################################################    
   
# Create Top_Card, Draw_Deck, Discard_Deck, Info_Tokens, and Wrong_Answer Nodes
top_card_name = "Top_Card"
top_card_node_name = "tc"
draw_deck_name = "Draw_Deck"
draw_deck_node_name = "dr_d"
discard_deck_name = "Discard_Deck"
discard_deck_node_name = "dis_d"
player_turn_name = "Player_Turn"
player_turn_node_name = "pt"

tc_node_name = db.nodes.create(name=top_card_name)
token.add(tc_node_name)
pt_node_name = db.nodes.create(name=player_turn_name)
token.add(pt_node_name)
dr_d_node_name = db.nodes.create(name=draw_deck_name)
deck.add(dr_d_node_name)
dis_d_node_name = db.nodes.create(name=discard_deck_name)
deck.add(dis_d_node_name)

k = 0

while k < num_info_tokens:
    key = k
    i_name = "Info_T_" + str(key+1)
    i_node_name = "i" + str(key+1)
    info_token_list_names[key] = i_name 
    info_token_list_nodes[key] = i_node_name
    i_node_name = db.nodes.create(name=i_name,used=False)
    token.add(i_node_name)
    k += 1
    
k = 0

while k < num_wrong_answer_tokens:
    key = k
    wa_name = "W_Answer_" + str(key+1)
    wa_node_name = "wa" + str(key+1)
    w_answer_token_list_names[key] = wa_name 
    w_answer_token_list_nodes[key] = wa_node_name
    wa_node_name = db.nodes.create(name=wa_name,used=False)
    token.add(wa_node_name)
    k += 1
    
# Establishing who goes first in what order
k = 0
q = 'MATCH (p:Player) RETURN p.name'
results = db.query(q, returns=(str))
while k < num_players:
    key = k
    key2 = k+1
    if key+1 == num_players:
        key2 = 0
    q = 'MATCH (p1:Player {name: "' + results[key][0] + '" }), (p2:Player {name: "' + results[key2][0] + '" }) CREATE (p1)-[:PLAYS_BEFORE]->(p2)'
    results_blank = db.query(q)
    if k == 0:
        q = 'MATCH (t:Token {name: "Player_Turn" }), (p:Player {name: "' + results[key][0] + '" }) CREATE (t)-[:PIS]->(p)'
    results_blank = db.query(q)
    k += 1 
       
#####################################################################
# SET-UP THE DECK
#####################################################################

pack_of_cards_obj = hanabi_deck.Hanabi_Deck(default_card_struct,num_colors_in_play)
game_deck = pack_of_cards_obj.deck
# Note: The deck is already generated pre-shuffled.

k = 0

for game_card in game_deck:
    key = k
    c_name = "Card_" + str(key+1)
    c_node_name = "c" + str(key+1)
    card_list_names[key] = c_name 
    card_list_nodes[key] = c_node_name
    # Pipe the Deck out into Neo4j
    c_node_name = db.nodes.create(name=c_name,order=key,value=game_card.number,color=game_card.color)
    card.add(c_node_name)
    
    dr_d_node_name.relationships.create("CONTAINS", c_node_name)
    
    if k == 0:
        tc_node_name.relationships.create("IS", c_node_name)
    
    k += 1

#####################################################################
# DEAL CARDS TO THE PLAYERS
#####################################################################    

done = 0
# NOTE:  The following code is extremely non-ideal.  Make it better when you can figure out how to do it cleaner
while done == 0:  
    q = 'MATCH (h:Hand) WHERE (h)-[:CONTAINS]->(:Card) RETURN h.name, count(*)'  
    results = db.query(q, returns=(str, int))
    
    if results.elements == []:
        #Add one card to each hand
        q = 'MATCH (h:Hand) RETURN h.name'
        results_2 = db.query(q, returns=(str))
        for r in results_2:
            name_of_the_hand = r[0]
            add_top_card_to_a_hand(name_of_the_hand,total_num_cards)
    else:
        for r in results:
            name_of_the_hand = r[0]
            cards_in_this_hand = r[1]
            while cards_in_this_hand < cards_per_hand:
                add_top_card_to_a_hand(name_of_the_hand,total_num_cards)
                cards_in_this_hand += 1
    done = check_num_cards_per_hand(cards_per_hand)
    # TODO: This way of implementing DONE is not ideal. Recommend improving/Fix later.   
     
#####################################################################
# PLAYERS OPEN THEIR EYES 
#####################################################################
q = 'MATCH (h:Hand), (c:Card), (p:Player) WHERE NOT (h)-[:CONTAINS]->(c) AND NOT (:Deck { name:"Draw_Deck" })-[:CONTAINS]->(c) AND (p)-[:CONTROLS]->(h) CREATE (h)-[:CAN_SEE]->(c)'
results = db.query(q)

#######################################################################
#######################################################################
######################## THE GAME BEGINS !!!!##########################
#######################################################################
#######################################################################



#####################################################################
# PLAYERS STARTS TO THINK
#####################################################################

