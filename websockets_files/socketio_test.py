import socketio
import os

# Initialize Socket.IO client
sio = socketio.Client()

"""
Logic Flow
-A user(admins, drivers and merchants) connects to the socketio server
- A merchant places an order
- The order is emitted as an event and the server assigns a room to the order id and emits an event to the admins and drivers
- Driver emits an event by placing a bid on an order and the server adds the driver to the room of that order
- An event is emited to the merchant for that room notifying them of a new bid on their order
- The merchant awards the bid to the driver of their choice and emits an event that is sent by the server to drivers for awarded or rejected bid
"""

"""
To achieve the logic above, there's need to track users connected to the socket
When users login, their connection will be established
"""

connected_users=[]

@sio.on("connect")
def on_connect(data):
    print(data)

# Event listeners
@sio.on('order_posted')
def on_product_posted(data):
    print("Product Posted:", data)

@sio.on('bid_placed')
def on_bid_placed(data):
    print("Bid Placed:", data)

@sio.on('bid_awarded')
def on_bid_awarded(data):
    print("Bid Awarded:", data)

try:
    # Connect to the server
    sio.connect(os.getenv("BACKEND_URL"))
    sio.wait()
except Exception as e:
    print(e)