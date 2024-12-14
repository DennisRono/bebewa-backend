import socketio

# Initialize Socket.IO client
sio = socketio.Client()



# Event listeners
@sio.on('order_posted')
def on_product_posted(data):
    print("Product Posted:", data)

# @sio.on('bid_placed')
# def on_bid_placed(data):
#     print("Bid Placed:", data)

# @sio.on('bid_awarded')
# def on_bid_awarded(data):
#     print("Bid Awarded:", data)

# Emit events for testing
def test_socketio():
    print("Testing Socket.IO events...")

#     # Join a room for a product
#     product_id = "12345"
#     sio.emit('join_room', {'product_id': product_id})
#     print(f"Joined room for product ID: {product_id}")

#     # Simulate placing a bid
#     sio.emit('bid_placed', {'product_id': product_id, 'buyer_id': 'buyer_001', 'bid_amount': 500})
#     print(f"Placed a bid for product ID: {product_id}")

#     # Simulate awarding a bid
#     sio.emit('bid_awarded', {'product_id': product_id, 'buyer_id': 'buyer_001', 'status': 'accepted'})
#     print(f"Awarded a bid for product ID: {product_id}")

# Run the test
# if __name__ == '__main__':
#     test_socketio()
try:
    # Connect to the server
    sio.connect('http://127.0.0.1:5555')
    sio.wait()
except Exception as e:
    print(e)