#!/opt/local/bin/python
#
#

# Start
# Figure out who's turn it is
q = 'MATCH (t:Token {name: "Player_Turn" }), (p:Player) WHERE (t)-[:IS]->(p) RETURN p.name'
results = db.query(q, returns=(str))
active_player_name = results[0][0]

# He looks at all the player's cards
q = 'MATCH (p:Player {name: "' + active_player_name +'" }), (c:Card) WHERE (p)-[:CAN_SEE]->(c) RETURN c.value, c.color, c.position, p.name'
results = db.query(q, returns=(int, str))
for r in results:
    r[0] = 
    
    
# He looks at what's been played
q = 'MATCH (d:Deck {name: "Discard_Deck" }), (c:Card) WHERE (d)-[:CONTAINS]->(c) RETURN c.value, c.color'
results = db.query(q, returns=(str))
active_player_name = results[0][0]

# He crunches through a couple of agreed to philosophies
# {Expanse of effort} 
# He decides to throw a card away, put a card down, or to give advice
# He organizes his/her own card order

# Next player Go & Repeat

# Game is done when either 1) there is one more round after draw deck = 0, 2) all the columns are done, or 3) there are 3 failures to put down.


