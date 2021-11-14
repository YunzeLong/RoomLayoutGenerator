import json
from typing import Dict
import sys
import random
from PIL import Image

class Item:
    def __init__(self, length, width, name, collision_count):
        self.length = length
        self.width = width
        self.name = name
        self.collision_count = collision_count
        
# Regarding collision_count, we will use 0 for available, 1 for overlappable collisions, and 2 for absolute no collision.


"""
block setting:
(dict, but presented as JSON string here)

{"number": 0,				    // block number
"xCoord": 0,				    // x-coordinate
"yCoord": 0,				    // y-coordinate
"collisionCount":0,			    // indicate whether stuff can be put, for non-colliding items, count =0
"item" : {"DeskAndChair"},		// indicate current item(s)
"NextTo": {"Wall", "AC"},		// indicate NextTo relationships
"Avoid": {"Bed"}			    // indicate items to avoid at this block
}
"""


NULL_ITEM = Item(0,0,"NULL",0)
WALL_ITEM = Item(0,0,"Wall",2)
AVOID_RANGE = 20



class RoomLayout:
    def __init__(self, x, y, items):
        self.block_list = dict()
        self.length = x
        self.width = y
        self.item_list = items
    # end init

    def generate_empty_block_list(self):
        counter = 0
        for i in range(self.length):
            for j in range(self.width):
                counter += 1
                self.block_list[(i,j)] = dict()
                self.block_list[(i,j)]["number"] = counter
                self.block_list[(i,j)]["xCoord"] = i
                self.block_list[(i,j)]["yCoord"] = j
                self.block_list[(i,j)]["collision_count"] = 0
                self.block_list[(i,j)]["item"] = list()
                self.block_list[(i,j)]["NextTo"] = list()
                self.block_list[(i,j)]["Avoid"] = list()

                # if on the boundary, insert WALL_ITEM, else as NULL
                self.update_block(i, j, WALL_ITEM) if(i == self.length-1 or j == self.width-1 or i == 0 or j == 0) else self.update_block(i, j, NULL_ITEM)
        return
    # end generate_empty_block_list       

    def replace_block_content(self, i, j, item):
        self.block_list[(i,j)]["item"] = list()
        self.block_list[(i,j)]["NextTo"] = list()
        self.block_list[(i,j)]["Avoid"] = list()
        self.block_list[(i,j)]["item"].append(item.name)
        self.block_list[(i,j)]["collision_count"] += item.collision_count
        return
    #end replace_block_content

    # code to update a block with item
    def update_block(self, i, j, item):
        self.block_list[(i,j)]["item"].append(item.name)
        self.block_list[(i,j)]["collision_count"] += item.collision_count
        return
    # end update block

    def put_item(self, x, y, item):
        for i in range(x, x+item.length):
            for j in range(y, y+item.width):
                self.update_block(i, j, item)
        return
    # end put_item
   
    def find_block(self, x, y):
        if x< 0 or y < 0 or x> self.width or y>self.length:
            sys.stderr.write("undefined block coordinate in find_block")
            exit(1)
        return self.block_list[(x,y)]
    # end find_block

    def check_collision(self, start_x, start_y, end_x, end_y, input_collision):
        if input_collision == 0:
            return True
        # if input has collision
        for i in range(start_x, end_x):
            for j in range(start_y, end_y):
                if(self.block_list[(i,j)]["collision_count"] + input_collision >= 2):
                    return False
        return True
    # end check_collision 

    def find_available_place(self, item):
        room_dim_x = self.length
        room_dim_y = self.width
        item_dim_x = item.length
        item_dim_y = item.width
        if(random.random()>0.5):
            for i in range(room_dim_x):
                # if i + item_dim_x > room_dim_x:
                #     return -1, -1
                if(random.random()>0.5):
                    for j in range(room_dim_y):
                        # if j + item_dim_y > room_dim_y:
                        #     return -1, -1
                        if(self.check_collision(i, j, i+item_dim_x, j+item_dim_y, item.collision_count)):
                            return i,j
                else:
                    for j in reversed(range(room_dim_y)):
                        if j - item_dim_y < 0:
                            continue
                        if(self.check_collision(i, j-item_dim_y, i+item_dim_x, j, item.collision_count)):
                            return i, j-item_dim_y
                    
        else:
            for i in reversed(range(room_dim_x)):
                # if i - item_dim_x < 0:
                #     return -1, -1
                if(random.random()>0.5):
                    for j in range(room_dim_y):
                        # if j + item_dim_y > room_dim_y:
                        #     return -1, -1
                        if(self.check_collision(i-item_dim_x, j, i, j+item_dim_y, item.collision_count)):
                            return i - item_dim_x,j
                else:
                    for j in reversed(range(room_dim_y)):
                        # if j - item_dim_y < 0:
                        #     return -1, -1
                        if(self.check_collision(i-item_dim_x, j-item_dim_y, i, j, item.collision_count)):
                            return i-item_dim_x, j-item_dim_y

        return -1, -1
        # end find_available_place


    # def find_available_place_transpose(self, item):
    #     room_dim_x = self.length
    #     room_dim_y = self.width
    #     item_dim_x = item.length
    #     item_dim_y = item.width
    #     if(random.random()>0.5):
    #         for j in range(room_dim_y):
    #             if(random.random()>0.5):
    #                 for i in range(room_dim_x):
    #                     if(self.check_collision(i, j, i+item_dim_x, j+item_dim_y, item.collision_count)):
    #                         return i,j
    #             else:
    #                 for i in reversed(range(room_dim_x)):
    #                     if(self.check_collision(i - item_dim_x, j, i, j+item_dim_y, item.collision_count)):
    #                         return i - item_dim_x, j
                    
    #     else:
    #         for j in reversed(range(room_dim_y)):
    #             if(random.random()>0.5):
    #                 for i in range(room_dim_x):
    #                     if(self.check_collision(i, j - item_dim_y, i+item_dim_x, j, item.collision_count)):
    #                         return i, j -item_dim_y
    #             else:
    #                 for i in reversed(range(room_dim_x)):
    #                     if(self.check_collision(i-item_dim_x, j-item_dim_y, i, j, item.collision_count)):
    #                         return i-item_dim_x, j-item_dim_y

    #     return -1, -1
    #     # end find_available_place_transpose

    # old definition
    def find_available_place_transpose(self, item):
        room_dim_x = self.length
        room_dim_y = self.width
        item_dim_x = item.length
        item_dim_y = item.width
        for j in range(room_dim_y):
            # if i + item_dim_x > room_dim_x:
            #     return -1, -1
            for i in range(room_dim_x):
                # if j + item_dim_y > room_dim_y:
                #     return -1, -1
                if(self.check_collision(i, j, i+item_dim_x, j+item_dim_y, item.collision_count)):
                    return i,j
        return -1, -1
        # end find_available_place_transpose
    

    def arrange_item_order_descending(self):
        item_size_dict = dict()
        for item in self.item_list:
            item_size_dict[item] = item.length * item.width
        sorted_dict = dict(sorted(item_size_dict.items(), key=lambda item: item[1]))
        return list(sorted_dict.keys()).reverse()
    # end arrange_item_order_descending        

    def print_room(self):
        room_dim_x = self.length
        room_dim_y = self.width
        for i in range(room_dim_x):
            for j in range(room_dim_y):
                blk = self.block_list[(i,j)]
                cc = blk["collision_count"]
                if(cc == 2):
                    print("*", end="")
                elif (cc == 0):
                    print(" ", end="")
                elif (cc==1):
                    last_item_index = len(blk["item"])-1
                    print(blk["item"][last_item_index][0], end="") # item[0] is NULL.
            print("\n")
        return
    # end print_room

    def naive_solve(self):
        for item in self.item_list:
            if(random.random()>0.5):
                x_pos, y_pos = self.find_available_place(item)
            else:
                x_pos, y_pos = self.find_available_place_transpose(item)
            # if(x_pos < 0 or y_pos < 0):
            #     sys.stderr.write("invalid x y")
            #     exit(1)
            self.put_item(x_pos, y_pos, item)
        self.print_room()
        return
    # end naive_solve

    def append_around(self, x, y, relation, content):
        max_x = self.length 
        max_y = self.width 

        if(y>=max_y or x >= max_x):
            return

        if(x-1 > 0):
            self.block_list[(x-1,y)][relation].append(content)
            if (y-1 >= 0):
                self.block_list[(x-1,y-1)][relation].append(content)
            if (y+1 < max_y):
                self.block_list[(x-1,y+1)][relation].append(content)

        if (y-1 >= 0):
            self.block_list[(x,y-1)][relation].append(content)
        if (y+1 < max_y):
            self.block_list[(x,y+1)][relation].append(content)

        if(x+1 < max_x):
            self.block_list[(x+1, y)][relation].append(content)
            if (y-1 >= 0):
                self.block_list[(x+1,y-1)][relation].append(content)
            if (y+1 < max_y):
                self.block_list[(x+1,y+1)][relation].append(content)

        return
    # end append_around

    def add_rules(self, rule_list):
        # rules are in the form: ["Avoid", "Bed", "Wall"]
        Avoid_dict_forward = dict()

        for rule in rule_list:
            relation = rule[0]
            if relation == "Avoid" or relation == "Avoids":
                A = rule[1]
                B = rule[2]
                Avoid_dict_forward[A] = B
                #Avoid_dict_backward[B] = A
        #Avoid_dict_backward = {value:key for key, value in Avoid_dict_forward.items()}

        for i in range(self.length):
            for j in range(self.width):
                for key in Avoid_dict_forward.items():
                    if key[1] in self.block_list[(i,j)]["item"]:
                        self.block_list[(i,j)]["Avoid"].append(key[0])
                        for x in range(AVOID_RANGE):
                            for y in range(AVOID_RANGE):
                                self.append_around(i+x, j+y, "Avoid", key[0])
                    elif key[0] in self.block_list[(i,j)]["item"]:
                        self.block_list[(i,j)]["Avoid"].append(key[1])
                        for x in range(AVOID_RANGE):
                            for y in range(AVOID_RANGE):
                                self.append_around(i+x, j+y, "Avoid", key[1])
        return
    # end add_rules
    
    def check_avoid(self, start_x, start_y, end_x, end_y, itemName):
        for i in range(start_x, end_x):
            for j in range(start_y, end_y):
                if itemName in self.block_list[(i,j)]["Avoid"]:
                    return False
        return True
    # end check_avoid

    def find_available_place_with_rules(self, item):
        room_dim_x = self.length
        room_dim_y = self.width
        item_dim_x = item.length
        item_dim_y = item.width
        if(random.random()>0.5):
            for i in range(room_dim_x):
                if(random.random()>0.5):
                    for j in range(room_dim_y):
                        if(self.check_collision(i, j, i+item_dim_x, j+item_dim_y, item.collision_count)
                        and self.check_avoid(i, j, i+item_dim_x, j+item_dim_y, item.name)
                        ):
                            return i,j
                else:
                    for j in reversed(range(room_dim_y)):
                        if(j - item_dim_y) < 0:
                            continue
                        if(self.check_collision(i, j-item_dim_y, i+item_dim_x, j, item.collision_count)
                        and self.check_avoid(i, j-item_dim_y, i+item_dim_x, j, item.name)
                        ):
                            return i, j-item_dim_y
                    
        else:
            for i in reversed(range(room_dim_x)):
                if(i-item_dim_x) < 0:
                    continue
                if(random.random()>0.5):
                    for j in range(room_dim_y):
                        if(self.check_collision(i-item_dim_x, j, i, j+item_dim_y, item.collision_count)\
                        and self.check_avoid(i-item_dim_x, j, i, j+item_dim_y, item.name)
                            ):
                            return i - item_dim_x,j
                else:
                    for j in reversed(range(room_dim_y)):
                        if(j-item_dim_y)<0:
                            continue
                        if(self.check_collision(i-item_dim_x, j-item_dim_y, i, j, item.collision_count)
                        and self.check_avoid(i-item_dim_x, j-item_dim_y, i, j, item.name)
                        ):
                            return i-item_dim_x, j-item_dim_y

        return -1, -1
        # end find_available_place_with_rules

    def find_available_place_with_rules_transpose(self, item):
        room_dim_x = self.length
        room_dim_y = self.width
        item_dim_x = item.length
        item_dim_y = item.width
        for j in range(room_dim_y):
            # if i + item_dim_x > room_dim_x:
            #     return -1, -1
            for i in range(room_dim_x):
                # if j + item_dim_y > room_dim_y:
                #     return -1, -1
                if(self.check_collision(i, j, i+item_dim_x, j+item_dim_y, item.collision_count)\
                and self.check_avoid(i, j, i+item_dim_x, j+item_dim_y, item.name)
                ):
                    return i,j
        return -1, -1
    # end find_available_place_with_rules_transpose


    def solve_with_avoid(self):
        for item in self.item_list:
            if(random.random()>0.5):
                x_pos, y_pos = self.find_available_place_with_rules(item)
            else:
                x_pos, y_pos = self.find_available_place_with_rules_transpose(item)
            # if(x_pos < 0 or y_pos < 0):
            #     sys.stderr.write("invalid x y")
            #     exit(1)
            self.put_item(x_pos, y_pos, item)
        #self.print_room()
        return
    # end solve_with_avoid

    def draw_solution(self):
        room_dim_x = self.length
        room_dim_y = self.width
        img = Image.new(mode="RGB", size = (room_dim_x, room_dim_y), color = (255,255,255))
        pixels = img.load()
        
        for i in range(room_dim_x):
            for j in range(room_dim_y):
                blk = self.block_list[(i,j)]
                cc = blk["collision_count"]
                if(cc == 2):
                    pixels[i,j] = (0,0,0)
                elif (cc == 0):
                    pass # do nothing, we want white.
                elif (cc==1):
                    last_item_index = len(blk["item"])-1
                    item_to_display = blk["item"][last_item_index]
                    if(item_to_display == "Bed"):
                        pixels[i,j] = (211, 211, 211)
                    if(item_to_display == "DeskAndChair"):
                        pixels[i,j] = (186, 140, 99)
                    if(item_to_display == "Couch"):
                        pixels[i,j] = (161, 61, 45)
                    if(item_to_display == "Shelf"):
                        pixels[i,j] = (115, 147, 179)
                    if(item_to_display == "Light"):
                        pixels[i,j] = (255, 255, 0)

        img.save("layout.png")
        img.show()
    # end draw solution

    def shuffle(self):
        self.generate_empty_block_list()
        random.shuffle(self.item_list)
    # end shuffle

Bed1 = Item(80, 140, "Bed", 1)
DeskAndChair1 = Item(60, 90, "DeskAndChair", 1)
Light1 = Item(10, 10, "Light", 0)
Couch1 = Item(30, 40, "Couch", 1)
Shelf1 = Item(80, 30, "Shelf", 1)

# Room1 = RoomLayout(20, 30, [Bed1, DeskAndChair1])
# Room1.generate_empty_block_list()
# Room1.naive_solve()


def test(param1, param2, param3):
    Room2 = RoomLayout(300, 200, [DeskAndChair1, Bed1, Light1, Couch1, Shelf1])
    Room2.generate_empty_block_list()
    custom_rule_list = [[param1, param2, param3]]
    Room2.add_rules(custom_rule_list)
    Room2.solve_with_avoid()
    Room2.draw_solution()
    

if(__name__ == "__main__"):
    test("Avoid", "DeskAndChair", "Wall")
