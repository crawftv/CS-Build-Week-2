import requests
import pickle
import json


class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None

    def size(self):
        return len(self.queue)


def bfs(starting_vertex, destination_vertex, player_graph):
    """
    Return a list containing the shortest path from
    starting_vertex to destination_vertex in
    breath-first order.
    """
    q = Queue()
    q.enqueue([starting_vertex])
    visited = set()

    while q.size() > 0:
        path = q.dequeue()
        v = path[-1]
        if v not in visited:
            if v == destination_vertex:
                return path
            visited.add(v)
            for direction in player_graph[v]["exits"].keys():
                if direction in ["n", "w", "e", "s"]:
                    path_copy = path.copy()
                    dd = player_graph[v]["exits"][direction]
                    if dd == "?":
                        pass
                    else:
                        path_copy.append(dd)
                        q.enqueue(path_copy)
                else:
                    break


def unexplored_directions(player_graph, room_id):
    unexplored_directions = []
    for i in ["n", "s", "e", "w"]:
        try:
            if player_graph[room_id]["exits"][i] == "?":
                unexplored_directions.append(i)
        except KeyError:
            pass
    return unexplored_directions


def find_unexplored_room(player_graph):
    """get a new route"""
    for i in player_graph:
        ii = unexplored_directions(player_graph, i)
        if len(ii) > 0:
            return i


def find_room_direction(response, player_graph, room_id, next_room):
    for i in response.json()["exits"]:
        if player_graph[room_id]["exits"][i] == next_room:
            return i


def movement(direction, API_KEY):
    movement_headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }
    m = requests.post(
        "https://lambda-treasure-hunt.herokuapp.com/api/adv/move/",
        headers=movement_headers,
        data=json.dumps({"direction": direction}),
    )
    return m


def wise_wizard(direction, room_number, API_KEY):
    movement_headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }
    m = requests.post(
        "https://lambda-treasure-hunt.herokuapp.com/api/adv/move/",
        headers=movement_headers,
        data=json.dumps({"direction": direction, "next_room_id": str(room_number)}),
    )
    return m


def pickup_treasure(treasure, API_KEY):
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"name": f"{treasure}"}

    response = requests.post(
        "https://lambda-treasure-hunt.herokuapp.com/api/adv/take/",
        headers=headers,
        data=json.dumps(data),
    )
    return response


def sell_treasure(ii,API_KEY):
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }
    data = {"name": f"{ii}", "confirm": "yes"}
    response = requests.post(
        "https://lambda-treasure-hunt.herokuapp.com/api/adv/sell/",
        headers=headers,
        data=json.dumps(data),
    )
    return response

def check_inventory(API_KEY):
    headers = {
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://lambda-treasure-hunt.herokuapp.com/api/adv/status/", headers=headers
    )
    return response.json()


def pickle_graph(player_graph):
    filename = "player_graph.pkl"
    outfile = open(filename, "wb")
    pickle.dump(player_graph, outfile)
    outfile.close()


def record_room_info(player_graph, response, direction=None, previous_room=None):
    opposite_map = {"n": "s", "s": "n", "e": "w", "w": "e"}
    r = response
    room_id = r.json()["room_id"]
    if room_id not in player_graph:
        player_graph[room_id] = {}
    player_graph[room_id]["title"] = r.json()["title"]
    player_graph[room_id]["description"] = r.json()["description"]
    player_graph[room_id]["coordinates"] = r.json()["coordinates"]
    player_graph[room_id]["messages"] = r.json()["messages"]
    player_graph[room_id]["elevation"] = r.json()["elevation"]
    player_graph[room_id]["terrain"] = r.json()["terrain"]

    if "exits" not in player_graph[room_id]:
        player_graph[room_id]["exits"] = {i: "?" for i in r.json()["exits"]}

    if player_graph[previous_room]["exits"][direction] == "?":
        player_graph[previous_room]["exits"][direction] = room_id
    if player_graph[room_id]["exits"][opposite_map[direction]] == "?":
        player_graph[room_id]["exits"][opposite_map[direction]] = previous_room

    return room_id
