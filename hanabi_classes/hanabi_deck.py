#!/opt/local/bin/python
# 

import random
import hanabi_card
     
class Hanabi_Deck(object):
    
    def __init__(self,card_dist_array,number_of_colors):
    
        color_set = ["White","Red","Blue","Green","Rainbow","Purple","Black","Orange","Brown","Pink"]
    
        # TODO: Add clause which gets out of loop if inputs are too wide/large
        number_of_cards = 0
        
        for num_cards in card_dist_array:            
            number_of_cards = number_of_cards + number_of_colors * num_cards
         
        self.number_of_cards = number_of_cards
        self.card_dist_array = card_dist_array
        self.number_of_colors = number_of_colors
        
        deck = []
        
        i = 0
        j = 0
        k = 0
        l = 0
        
        while i < len(card_dist_array):
            j=0
            while j < card_dist_array[i]:
                k=0
                while k < number_of_colors:
                    temp = hanabi_card.Hanabi_Card(i+1,color_set[k])
                    deck.append(temp)
                    #print("number:" + str(i+1) + ", color_set:" + str(color_set[k]))
                    k=k+1
                    l=l+1
                j=j+1
            i=i+1
            
        random.shuffle(deck)
           
        self.deck = deck

#########################################################################################
#    def ready_deck(self):
#        random.shuffle(self.deck)
#        #self.deck = deck

#########################################################################################
