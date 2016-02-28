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

from operator import itemgetter, attrgetter, methodcaller
import sys

###############################################################
# DEFINE FUNCTION: 
###############################################################


################## ADD TOP CARD TO THE HAND ###################
def add_top_card_to_a_hand(name_of_the_hand,total_num_cards):

    # Find the name and order # of the top card
    q = 'MATCH (c:Card) WHERE (:Token { name:"Top_Card" })-[:IS]->(c) RETURN c.name, c.order'
    results_c_order = db.query(q, returns=(str, int))
    # print results_c_order[0]
    
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
        
        # Add card attributes as perceived by the player
        q = 'MATCH (c:Card {name: "' + name_of_old_top_card + '" }) SET c.hand_order = { ' + 10 +'}'
        results_blank = db.query(q)
        
        # Add the impressions the player has of the new card
        ci_name = "Card_Idea_Next" # THERE SHOULD BE A WAY TO DO THIS
        ci_node_name = db.nodes.create(name=ci_name, worth=0)
        card.add(ci_node_name)
        q = 'MATCH (h:Hand {name: "' + name_of_the_hand + '" }), (p:Player), (c:Card {name: "' + name_of_old_top_card +'"), (ci:Card {name: "'+ ci_name +'"}) WHERE (p)-[:CONTROLS]->(h) CREATE (p)-[:KNOWS]->(ci) AND (ci)-[:REPRESENTS]->(c)'
        results = db.query(q)
        
         
################## SEE IF THERE ARE LESS THAN X NUMBER OF CARDS IN THE HANDS ###################
def check_num_cards_per_hand(cards_per_hand):
    done = 1
    q = 'MATCH (h:Hand) RETURN h.name'
    results_3 = db.query(q, returns=(str))
    for r in results_3:
        name_of_the_hand = r[0]
        #print r[0]
        q = 'MATCH (h:Hand {name: "' + name_of_the_hand + '" }), (c:Card) WHERE (h)-[:CONTAINS]->(c) RETURN count(*)'
        results_4 = db.query(q, returns=(int))
        if results_4[0][0] != cards_per_hand:
            done = 0
    return done    
    
###################################### REMOVE A CARD FROM YOUR HAND ########################################      
def remove_a_card_from_hand(card_name):

    q = 'MATCH (c:Card {name: "' + card_name + '"}, (ci:Card) WHERE (ci)-[:REPRESENTS]->(c) DELETE ci'
    results = db.query(q)
    
    q = 'MATCH (c:Card {name: "' + card_name + '"}, (h:Hand) WHERE (h)-[rel:CONTAINS]->(c) DELETE rel'
    results = db.query(q)
    
    q = 'MATCH (c:Card {name: "' + card_name + '"} REMOVE c.hand_order'
    results = db.query(q)
             
###################################### PLACE CARD IN DISCARD PILE ##########################################      
def discard_a_card(card_name):
    
    q = 'MATCH (c:Card {name: "' + card_name + '"}, (t:Token {name: "Discard_Deck"}) CREATE (t)-[:CONTAINS]->(c)'
    results = db.query(q)
    
    # Flip Info Token
    q = 'MATCH (t:Token {type: "Info"} WHERE t.used == True RETURN t.name'
    results = db.query(q)
    if results != []:
        q = 'MATCH (t:Token {name: "' + results[0] + '} SET t.used = {False}'
        results_2 = db.query(q)
    
######################################## PLAY A CARD ###########################################      
def play_a_card(card_name):
    
    q = 'MATCH (c:Card {name: "' + card_name + '"} RETURN c.color, c.value'
    results = db.query(q, returns=(str, int))
    card_color = results[0][0]
    card_value = results[0][1]
    
    q = 'MATCH (d:Deck {color: "' + card_color + '"} RETURN d.name'
    results = db.query(q, returns=(str))
    
    if results == []:
        if card_value == 1:
            col_node_name = card_color + ' Column'
            column_node_name = db.nodes.create(name=col_node_name)
            deck.add(col_node_name)
            
            q = 'MATCH (d:Deck {color: "' + card_color + '"}, (c:Card {name: "' + card_name + '"} CREATE (d)-[:CONTAINS]->(c)'
            results_2 = db.query(q)
            
            q = 'MATCH (c:Card {name: "' + card_name + '" }) SET c.column_order = {"Top"}'
            results_2 = db.query(q)
        else:
            q = 'MATCH (t:Token {type: "Wrong Answer"} WHERE t.used == False RETURN t.name'
            results_3 = db.query(q)
            if results_3 == []:
                q = 'MATCH (c:Card {name: "' + card_name + '"}, (t:Token {name: "Discard_Deck"}) CREATE (t)-[:CONTAINS]->(c)'
                results_9 = db.query(q)
                
                # THIS IS THE END OF THE GAME !!!!
                end_and_score_game()
                
            else:
                q = 'MATCH (t:Token {name: "' + results_3[0] + '"} SET t.used = {True}'
                results_4 = db.query(q)
    else:
        q = 'MATCH (d:Deck {color: "' + card_color + '"}, (c:Card {column_order: "Top"}) WHERE (d)-[:CONTAINS]->(c) RETURN c.name, c.value'
        results_5 = db.query(q, returns=(str,int))
        old_col_card_in_color_name = results_5[0][0]
        old_col_card_in_color_value = results_5[0][0]
        
        if card_value == old_col_card_in_color_value + 1:
            
            q = 'MATCH (d:Deck {color: "' + card_color + '"}, (c:Card {name: "' + card_name + '"} CREATE (d)-[:CONTAINS]->(c)'
            results_6 = db.query(q)
            q = 'MATCH (c:Card {name: "' + card_name + '" }) SET c.column_order = {"Top"}'
            results_6 = db.query(q)
            q = 'MATCH (c:Card {name: "' + old_col_card_in_color_name + '" }) REMOVE c.column_order'
            results_6 = db.query(q)
        else: 
            q = 'MATCH (t:Token {type: "Wrong Answer"} WHERE t.used == False RETURN t.name'
            results_7 = db.query(q)
            if results_7 == []:
                q = 'MATCH (c:Card {name: "' + card_name + '"}, (t:Token {name: "Discard_Deck"}) CREATE (t)-[:CONTAINS]->(c)'
                results_9 = db.query(q)
                # THIS IS THE END OF THE GAME !!!!
                end_and_score_game()
            else:
                q = 'MATCH (t:Token {name: "' + results_7[0] + '"} SET t.used = {True}'
                results_8 = db.query(q)

###################################### PLACE CARD IN DISCARD PILE ##########################################      
def give_player_information(player_who_gets_info,info_type,info):
    
    # Flip Info Token
    q = 'MATCH (t:Token {type: "Info"} WHERE t.used == False RETURN t.name'
    results = db.query(q)
    
    if results == []:
        print "ERROR !!!! YOU HAVE NO MORE INFO TOKEN TO FLIP OVER!!!!!"
        # TODO: PUT SOMETHING ELSE IN HERE   
    else:
        q = 'MATCH (t:Token {name: "' + results[0] + '"} SET t.used = {True}'
        results = db.query(q)
    
        if info_type == "Color":
            q = 'MATCH (p:Player {name: "' + player_who_gets_info + '"}, (ci:Card), (c:Card {color: "' + info + '") WHERE (p)-[:KNOWS]->(ci) AND (ci)-[:REPRESENTS]->(c) SET ci.color == {' + info + '}'
            results = db.query(q)
        else if info_type == "Value":
            q = 'MATCH (p:Player {name: "' + player_who_gets_info + '"}, (ci:Card), (c:Card {value: "' + info + '") WHERE (p)-[:KNOWS]->(ci) AND (ci)-[:REPRESENTS]->(c) SET ci.value == {' + info + '}'
            results = db.query(q)
        else:
            print "ERROR !!!! YOU NEVER SHOULD HAVE ARRIVED HERE !!!!"
            # TODO: PUT SOMETHING ELSE IN HERE     
    
    
######################################## SORT HAND ###########################################      
def sort_hand(playing_player_name):
    
    # Find all the cards of a player
    q = 'MATCH (p:Player {name: "' + playing_player_name + '" }) (h:Hand), (c:Card), (ci:Card) WHERE (p)-[:CONTROLS]-(h) AND (h)-[:CONTAINS]-(c) AND (ci)-[:REPRESENTS]->(c) RETURN c.name, ci.worth, c.hand_order'
    results = db.query(q, returns=(str,int,int))
    # Sort his cards by the perceived worth of each card
    new_results =  sorted(results, key=itemgetter(1), reverse=True)
    k = 0
    # Re-order the cards
    for c in new_results:
        q = 'MATCH (c:Card {name: "' + c[0] + '"} SET c.hand_order = { "' + k + '"}'
        results = db.query(q)
        k += 1
        
######################################## END GAME: SCORE TABLE ###########################################      
def end_and_score_game():
    
    q = 'MATCH (c:Card {column_order: "Top" }) RETURN c.value'
    results = db.query(q, returns=(int) )
    k = 0
    for r in results:
        k = r + k
    print "\nTHE GAME IS COMPLETE. THE SCORE WAS : " + k +".\n\n"
    
    sys.exit()
    
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
    i_node_name = db.nodes.create(name=i_name,type:"Info",used=False)
    token.add(i_node_name)
    k += 1
    
k = 0

while k < num_wrong_answer_tokens:
    key = k
    wa_name = "W_Answer_" + str(key+1)
    wa_node_name = "wa" + str(key+1)
    w_answer_token_list_names[key] = wa_name 
    w_answer_token_list_nodes[key] = wa_node_name
    wa_node_name = db.nodes.create(name=wa_name,type:"Wrong Answer",used=False)
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
        q = 'MATCH (t:Token {name: "Player_Turn" }), (p:Player {name: "' + results[key][0] + '" }) CREATE (t)-[:IS]->(p)'
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


########################################################################
####                  PLAYERS OPEN THEIR EYES                       ####
########################################################################

# See the other players Cards
q = 'MATCH (h:Hand), (c:Card), (p:Player) WHERE NOT (h)-[:CONTAINS]->(c) AND NOT (:Deck { name:"Draw_Deck" })-[:CONTAINS]->(c) AND (p)-[:CONTROLS]->(h) CREATE (p)-[:CAN_SEE]->(c)'
results = db.query(q)

# Add players thoughts on cards
q = 'MATCH (p:Player) RETURN p.name'  
results = db.query(q, returns=(str))
for p in results:
    q = 'MATCH (p:Player {name: "' + p[0] + '" }), (h:Hand), (c:Card) WHERE (p)-[:CONTROLS]-(h) AND (h)-[:CONTAINS]-(c) RETURN c.name
    results_2 = db.query(q, returns=(str))
    k = 0
    for pc in results_2:
        key = k
        ci_name = "Card_Idea_" + str(key+1)
        ci_node_name = db.nodes.create(name=ci_name)
        card.add(ci_node_name)
        q = 'MATCH (p:Player {name: "' + p[0] + '" }), (c:Card {name: "' + pc[0] +'"), (ci:Card {name: "'+ ci_name +'"}) CREATE (p)-[:KNOWS]->(ci) AND (ci)-[:REPRESENTS]->(c)'
        results = db.query(q)
    
    sort_hand(p[0])
                 
#######################################################################
#######################################################################
######################## THE GAME BEGINS !!!!##########################
#######################################################################
#######################################################################