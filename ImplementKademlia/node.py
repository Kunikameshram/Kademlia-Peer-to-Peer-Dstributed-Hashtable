import socket
import threading
import heapq
from operator import itemgetter
from graphviz import Digraph

class Node():
    
    def __init__(self, node_id, port, ip):
        self.node_id = node_id
        self.port = port
        self.ip = ip
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        
    def cal_distance(self, node):
        return self.node_id ^ node.node_id
    
    def __repr__(self):
        return f"Node({self.node_id}, {self.ip}, {self.port})"
        
    def listen(self):
        
        while True:
            message, addr = self.sock.recvfrom(1024)  # Receive up to 1024 bytes
            print(f"Node {self.node_id} received message: '{message.decode()}' from {addr}")
            
    def send_message(self, target_ip, target_port, message):
        
        self.sock.sendto(message.encode(), (target_ip, target_port))
        print(f"Node {self.node_id} sent message: '{message}' to {target_ip}:{target_port}")
        
class ClosestNodeDict():
    
    def __init__(self, ref_node, maxsize):
        self.ref_node = ref_node
        self.maxsize = maxsize
        self.heap = []
        self.contacted = set()      
        
    def add(self, nodes):
        
        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            distance = self.ref_node.cal_distance(node)
            if node.node_id not in self.get_ids():
                heapq.heappush(self.heap, (distance, node))
    
    def return_closest(self):
        """Remove and return the closest node."""
        return heapq.heappop(self.heap)[1] if self.heap else None  
        
    def mark_contacted(self, node):
        """Mark a node as contacted."""
        self.contacted.add(node.id)

    def get_uncontacted(self):
        """Get uncontacted nodes."""
        return [node for _, node in self.heap if node.id not in self.contacted]

    def get_ids(self):
        """Return a list of all node IDs in the heap."""
        return [node.id for _, node in self.heap]

    def __len__(self):
        """Get the number of nodes in the heap (up to maxsize)."""
        return min(len(self.heap), self.maxsize)

    def __iter__(self):
        """Iterate through nodes in the heap."""
        return iter(map(itemgetter(1), heapq.nsmallest(self.maxsize, self.heap)))
    
    def visualize_heap_graphviz(self):
        """Visualize the heap as a tree using Graphviz."""
        dot = Digraph()
        
        def add_node_to_graph(index=0):
            """Add the current node and recursively add its children."""
            if index < len(self.heap):
                node = self.heap[index]
                node_id = f"Node {node[1].node_id}"
                dot.node(node_id, f"ID: {node[1].node_id}\nDist: {node[0]}")
                
                left_index = 2 * index + 1
                right_index = 2 * index + 2
                
                if left_index < len(self.heap):
                    left_node = f"Node {self.heap[left_index][1].node_id}"
                    dot.edge(node_id, left_node)
                    add_node_to_graph(left_index)
                
                if right_index < len(self.heap):
                    right_node = f"Node {self.heap[right_index][1].node_id}"
                    dot.edge(node_id, right_node)
                    add_node_to_graph(right_index)
        
        add_node_to_graph()
        dot.render('heap_tree', format='png', view=True)
    
if __name__ == "__main__":
    # Create a couple of nodes
    node1 = Node(1, 5001, "127.0.0.1")
    node2 = Node(2, 5002, "127.0.0.1")
    
    # Create a closest node dictionary for node1
    closest_nodes = ClosestNodeDict(node1, 3)
    
    # Add node2 to the closest node dictionary
    closest_nodes.add([node2])
    
    # # Start listening for messages from other nodes
    # threading.Thread(target=node1.listen, daemon=True).start()
    # threading.Thread(target=node2.listen, daemon=True).start()
    
    # # Send a message from node1 to node2
    # node1.send_message("127.0.0.1", 5002, "Hello, Node 2!")
    
    # # Send a message from node2 to node1
    # node2.send_message("127.0.0.1", 5001, "Hello, Node 1!")
    
    closest_nodes.visualize_heap_graphviz()
    