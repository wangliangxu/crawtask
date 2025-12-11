
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/nodes"

def test_nodes():
    print("Waiting for server to start...")
    time.sleep(2) 
    try:
        # Create
        print("Creating node...")
        node_data = {
            "name": "Test Node",
            "host": "192.168.1.100",
            "port": 22,
            "username": "admin",
            "password": "secretpassword",
            "ssh_key_path": "/path/to/key"
        }
        res = requests.post(BASE_URL + "/", json=node_data)
        if res.status_code == 200:
            print("Create Success:", res.json())
            node_id = res.json()["id"]
        elif res.status_code == 400:
             print("Node already exists, proceeding to list...")
             # Try to find it in list
             all_nodes = requests.get(BASE_URL + "/").json()
             for n in all_nodes:
                 if n["name"] == "Test Node":
                     node_id = n["id"]
                     break
             else:
                 print("Could not find existing node id")
                 return
        else:
            print("Create Failed:", res.text)
            return

        # Read List
        print("\nListing nodes...")
        res = requests.get(BASE_URL + "/")
        print("Nodes:", res.json())

        # Read Detail
        print(f"\nReading node {node_id}...")
        res = requests.get(f"{BASE_URL}/{node_id}")
        print("Node Detail:", res.json())

        # Delete
        print(f"\nDeleting node {node_id}...")
        res = requests.delete(f"{BASE_URL}/{node_id}")
        if res.status_code == 200:
             print("Delete Success")
        else:
             print("Delete Failed:", res.text)
             
    except Exception as e:
        print("Test Error:", e)

if __name__ == "__main__":
    test_nodes()
