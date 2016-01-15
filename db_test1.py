#!/opt/local/bin/python
# 
# 

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
 
db = GraphDatabase("http://localhost:7474", username="neo4j", password="mypassword")
 
q1 = 'START n = node(*) OPTIONAL MATCH n-[r]-() WHERE (ID(n)>0 AND ID(n)<10000) DELETE n, r'
results = db.query(q1) 

# TODO: Set this up with a running check to ensure that all the pre-existing data has
#       been removed.

 
# Create some nodes with labels
user = db.labels.create("User")
u1 = db.nodes.create(name="Marco")
user.add(u1)
u2 = db.nodes.create(name="Daniela")
user.add(u2)
 
beer = db.labels.create("Beer")
b1 = db.nodes.create(name="Punk IPA")
b2 = db.nodes.create(name="Hoegaarden Rosee")
# You can associate a label with many nodes in one go
beer.add(b1, b2)

# User-likes->Beer relationships
u1.relationships.create("likes", b1)
u1.relationships.create("likes", b2)
u2.relationships.create("likes", b1)
# Bi-directional relationship?
u1.relationships.create("friends", u2)

q = 'MATCH (u:User)-[r:likes]->(m:Beer) WHERE u.name="Marco" RETURN u, type(r), m'
# "db" as defined above
results = db.query(q, returns=(client.Node, str, client.Node))
for r in results:
    print("(%s)-[%s]->(%s)" % (r[0]["name"], r[1], r[2]["name"]))
# The output:
# (Marco)-[likes]->(Punk IPA)
# (Marco)-[likes]->(Hoegaarden Rosee)
