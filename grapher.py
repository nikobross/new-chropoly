import tkinter as tk
import networkx as nx
import numpy as np
import main

G = nx.Graph()
verticies = []
edges = []
dragging = None

class Vertex:
    
    def __init__(self, name, x, y):
        
        self.name = name
        self.x = x
        self.y = y

class Edge:
        def __init__(self, name, x1, y1, x2, y2):
            
            self.name = name
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2


def find_closest_vertex(x, y):
    global verticies
    closest_vertex = None
    min_distance = float('inf')
    for vertex in verticies:
        distance = np.sqrt((x - vertex.x)**2 + (y - vertex.y)**2)
        if distance < min_distance:
            min_distance = distance
            closest_vertex = vertex
    return closest_vertex

def start_drag(event):
    global dragging
    closest_vertex = find_closest_vertex(event.x, event.y)
    if closest_vertex is not None:
        dragging = closest_vertex

def drag(event):
    global dragging
    if dragging:
        original_x = dragging.x
        original_y = dragging.y
        dragging.x = event.x
        dragging.y = event.y
        update_edges(original_x, original_y, event.x, event.y)

def update_edges(original_x, original_y, new_x, new_y):
    global edges
    for edge in edges:
        if edge.x1 == original_x and edge.y1 == original_y:
            edge.x1 = new_x
            edge.y1 = new_y
        if edge.x2 == original_x and edge.y2 == original_y:
            edge.x2 = new_x
            edge.y2 = new_y

def stop_edge(event):
    global edge_start
    if edge_start is not None:
        closest_vertex = find_closest_vertex(event.x, event.y)
        if closest_vertex is not None:
            if edge_start != closest_vertex:
                edges.append(Edge(len(edges) + 1, edge_start.x, edge_start.y, closest_vertex.x, closest_vertex.y))
                G.add_edge(edge_start.name, closest_vertex.name)
                edge_start = None

def add_vertex(event):
    global verticies
    verticies.append(Vertex(len(verticies) + 1, event.x, event.y))
    G.add_node(len(verticies) + 1)

def refresh_loop():
    for item in canvas.find_all():
        canvas.delete(item)

    for edge in edges:
            canvas.create_line(edge.x1, edge.y1, edge.x2, edge.y2, fill='white', width=2)

    for vertex in verticies:
        canvas.create_oval(vertex.x - 10, vertex.y - 10, vertex.x + 10, vertex.y + 10, fill='blue')
        canvas.create_text(vertex.x, vertex.y, text=str(vertex.name), fill='white')
    
    canvas.after(10, refresh_loop)

def start_edge(event):
    global edge_start
    closest_vertex = find_closest_vertex(event.x, event.y)
    if closest_vertex is not None:
        edge_start = closest_vertex

def stop_drag(event):
    global dragging
    dragging = None


root = tk.Tk()

root.title("Grapher")

result_var = tk.StringVar()

calculate_button = tk.Button(root, text="Calculate", command=lambda: result_var.set(main.write_formula(main.chromatic_polynomial_coefficients(G))), font=("Arial", 30))
calculate_button.pack(side=tk.BOTTOM, anchor=tk.SE)

result_label = tk.Label(root, textvariable=result_var, font=("Arial", 40))
result_label.pack(side=tk.BOTTOM)
result_label.pack(side=tk.BOTTOM)

canvas = tk.Canvas(root, width=800, height=600)
canvas.bind("<Shift-Button-1>", start_edge)
canvas.bind("<Shift-ButtonRelease-1>", stop_edge)
canvas.bind("<Double-Button-1>", add_vertex)
canvas.bind("<Button-1>", start_drag)
canvas.bind("<B1-Motion>", drag)
canvas.bind("<ButtonRelease-1>", stop_drag)
canvas.pack()

canvas.after(10, refresh_loop)


root.mainloop()