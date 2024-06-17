import tkinter as tk
import networkx as nx
import numpy as np
import main

G = nx.Graph()

edges_to_draw = {}
vertex_dict = {}
edge_dict = {}
node_labels = {}

edge_start = None

def start_edge(event):
    global edge_start
    closest = canvas.find_closest(event.x, event.y)
    while closest and canvas.type(closest[0]) not in ['oval', 'text']:  # Check if the closest item is a vertex
        closest = canvas.find_closest(event.x + 1, event.y + 1)  # Find the next closest item
    if closest:
        edge_start = closest[0]
        print('Edge start:', edge_start)

def stop_edge(event):
    global edge_start
    if edge_start is not None and canvas.type(edge_start) == 'oval':
        closest = canvas.find_closest(event.x, event.y)
        while closest and canvas.type(closest[0]) not in ['oval', 'text']:  # Check if the closest item is a vertex
            closest = canvas.find_closest(event.x + 1, event.y + 1)  # Find the next closest item
        if closest and canvas.type(closest[0]) in ['oval', 'text']:
            if edge_start == closest[0]:  # Check if the edge starts and ends at the same vertex
                return  # Do not create an edge if it starts and ends at the same vertex
            x1, y1, _, _ = canvas.coords(edge_start)
            x2, y2, _, _ = canvas.coords(closest[0])
            
            edges_to_draw[(edge_start, closest[0])] = (x1, y1, x2, y2)
            G.add_edge(node_labels[edge_start], node_labels[closest[0]])
            edge_start = None

def add_vertex(event):
    global label_counter
    node = (event.x, event.y)
    G.add_node(label_counter)
    radius = 10  # Increase this value to increase the size of the vertices
    vertex = canvas.create_oval(event.x - radius, event.y - radius, event.x + radius, event.y + radius, fill='blue')
    label = canvas.create_text(event.x, event.y, text=str(label_counter), fill='white')
    vertex_dict[vertex] = label  # Store the vertex and label pair in the dictionary
    node_labels[vertex] = label_counter
    label_counter += 1

def start_drag(event):
    global dragging
    closest = canvas.find_closest(event.x, event.y)
    if closest:  # Check if the tuple is not empty
        closest = closest[0]
        if canvas.type(closest) == 'text':
            overlapping = canvas.find_overlapping(*canvas.bbox(closest))
            if overlapping:  # Check if the tuple is not empty
                closest = overlapping[0]
        if canvas.type(closest) == 'oval' or canvas.type(closest) == 'text':
            dragging = closest

def stop_drag(event):
    global dragging
    if dragging:
        move_edge()  # Move the edge when dragging is stopped
    dragging = None

def move_edge():
    global edges_to_draw
    for (start, end), (x1, y1, x2, y2) in list(edges_to_draw.items()):
        if start == dragging or end == dragging:
            x1, y1, _, _ = canvas.coords(start)
            x2, y2, _, _ = canvas.coords(end)
            edges_to_draw[(start, end)] = (x1, y1, x2, y2)

def drag(event):
    if dragging:
        x1, y1, x2, y2 = canvas.coords(dragging)
        dx = event.x - x1
        dy = event.y - y1
        canvas.move(dragging, dx, dy)  # Move the vertex
        canvas.move(vertex_dict[dragging], dx, dy)  # Move the corresponding label

def refresh_loop():
    # Delete all lines
    for item in canvas.find_all():
        if canvas.type(item) == 'line':
            canvas.delete(item)

    # Draw the edges stored in the dictionary
    for (start, end), (x1, y1, x2, y2) in edges_to_draw.items():
        canvas.create_line(x1, y1, x2, y2)

    # Call the refresh loop again after a delay
    canvas.after(100, refresh_loop)  # Adjust the delay as needed

dragging = None

label_counter = 1

root = tk.Tk()

result_var = tk.StringVar()

# Create the button
calculate_button = tk.Button(root, text="Calculate", command=lambda: result_var.set(main.write_formula(main.chromatic_polynomial_formula(G))))
calculate_button.pack(side=tk.BOTTOM, anchor=tk.SE)

# Create the label
result_label = tk.Label(root, textvariable=result_var)
result_label.pack(side=tk.BOTTOM)

canvas = tk.Canvas(root, width=500, height=500)
canvas.bind("<Shift-Button-1>", start_edge)
canvas.bind("<Shift-ButtonRelease-1>", stop_edge)
canvas.bind("<Double-Button-1>", add_vertex)
canvas.bind("<Button-1>", start_drag)
canvas.bind("<B1-Motion>", drag)
canvas.bind("<ButtonRelease-1>", stop_drag)
canvas.pack()

# Start the refresh loop
canvas.after(100, refresh_loop)

root.mainloop()