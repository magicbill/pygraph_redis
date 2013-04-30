#/usr/bin/env python

from datetime import datetime
import random
from multiprocessing import Process
import sys

#importing directed_graph
from pygraph_redis.directed_graph import Directed_graph
import redis

import logging

try: 
    sys.argv[1]
except IndexError:
    node_number = 1000
    print "using the default number of nodes: 1000"
    print "you can change it by passing an arg to the script"
else:
    node_number = int(sys.argv[1])

#max number of successors
max_number_successors = 10
#max number of predecessors
max_number_predecessors = 10

#empty lists (initialization)
nodes = []
successors = []
predecessors = []

OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'

#some fixed attributs
fix_attributes = {u'jack': set([u'1',u'2']), u'spare': u'youpi'}

#function transforming <number> -> node_<number>
def create_name_from_number(integer):
    return u'node_' + str(integer)

#function generating the graph in python structures
def generate_tree(node_number):

    #we create node_number of nodes
    for node in range(node_number):
        #we create a nice name for the node (node_<number>)
        node_name = create_name_from_number(node)
        #we add it to the node
        nodes.append(node_name)
        successors_node = []
        #for each nodes, we create a random number of successors < max_number_successors
        for j in range(random.randint(1, max_number_successors)):
            successor_name = create_name_from_number(random.randint(1, node_number))
            successors_node.append(successor_name)
        predecessors_node = []
        #for each nodes, we create a random number of predecessors < max_number_predecessors
        for j in range(random.randint(1, max_number_predecessors)):
            predecessor_name = create_name_from_number(random.randint(1, node_number))
            predecessors_node.append(predecessor_name)
        #we add the successors of the node in the list of successors lists (same with the predecessors)
        successors.append(successors_node)
        predecessors.append(predecessors_node)

print OKBLUE + "creating " + str(node_number)  + " nodes"
#calling the generation function
generate_tree(node_number)

#creating the redis connexion
r_server = redis.Redis("localhost")

#creating a basic logger
logging.basicConfig(format = u'%(message)s')
logger = logging.getLogger(u'redis')
logger.parent.setLevel(logging.CRITICAL)

#creating the graph object
graph = Directed_graph(r_server, u'uniq', logger)

#we define two process to write the nodes
def process_one():
    for i in range(0,node_number,2):
        graph.write_on_node(nodes[i],successors[i],predecessors[i],fix_attributes)

def process_two():
    for i in range(1,node_number,2):
        graph.write_on_node(nodes[i],successors[i],predecessors[i],fix_attributes)

#we get the date before the insertion
t1 = datetime.now()
#create and launch the two processes
print OKBLUE + "starting the insertion"
p1 = Process(target=process_one)
p2 = Process(target=process_two)
p1.start()
p2.start()
p1.join()
p2.join()

#when the two processes are ended
#we get the date after the insertion 
t2 = datetime.now()
c = t2 - t1

#we print the number of node inserted per second
print  OKBLUE + "insertion completed"
print  OKGREEN + "####\nadding " + str(node_number / c.total_seconds()) + " nodes/second\n####"

#we do exactly the same to delete the inserted nodes
def process_one():
    for i in range(0,node_number,2):
        graph.remove_node(nodes[i])

def process_two():
    for i in range(1,node_number,2):
        graph.remove_node(nodes[i])

t1 = datetime.now()
print OKBLUE + "starting deleting the nodes"
p1 = Process(target=process_one)
p2 = Process(target=process_two)
p1.start()
p2.start()
p1.join()
p2.join()

t2 = datetime.now()
c = t2 - t1
print OKBLUE + "delete completed"
print OKGREEN + "####\nremoving " + str(node_number / c.total_seconds()) + " nodes/second\n####"