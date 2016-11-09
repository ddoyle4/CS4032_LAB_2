from concurrent.futures import ThreadPoolExecutor
import errno
import socket                                         
import time
import sys
import threading
import collections

#GLOBAL VARIABLES
#flag for whether or not to kill the main service
kill_service_value = False

class tcp_server():

	def __init__(self, port, connQueue, server_threads = 5):
		self.server_socket = self.init_server_socket(port, connQueue)
		self.pool = ThreadPoolExecutor(server_threads)

		#configuration settings for server
		self.server_info = {
			"sid": "11315921"
		}

	def serve(self):
		"""
		Main server loop. Runs while running is True. Checks kill_service_value 
		to check if kill flag has been set, and terminates if it has
		"""
		print("Server running")
		running = True
		kill_service_lock = threading.Lock()	#kill_service_value thread lock
		while running:
			#non-blocking socket accept implementation
			try:	#accept if there is a connection

				client_socket, client_addr = self.server_socket.accept()      

				print("servicing new connection")

				#launch new client handler thread
				self.pool.submit(
					client_handler, 
					client_socket, 
					client_addr, 
					self.server_info, 
					kill_service_lock
				)

			except IOError as e:  #no connections would block, so sleep
				if e.errno == errno.EWOULDBLOCK:
					time.sleep(0.05) 

			#check for kill flag
			if kill_service_lock.acquire(False):
				if kill_service_value:
					running = False
					self.pool.shutdown()
					print("KILLING SERVICE...")
				kill_service_lock.release()
				

		self.server_socket.close()
		print("Server has been shut down")

	def init_server_socket(self, port, connQueue):
		"""
		Initialises the server socket.
		Params: 
			port: int port number
			connQueue: int number of connections to queue on socket

		NOTE - this also sets the configuration settings dict 
		for the server.
		"""
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		#TODO remove this hard coded host in production
		server_host = socket.gethostname()                           
		server_port = port
		server_socket.bind((server_host, server_port))                                  
		server_socket.listen(connQueue)                                           
		server_socket.setblocking(0)

		return server_socket


def client_handler(client_socket, client_addr, server_info, lock):
	"""
	Client handler method. To be run in seperate thread.
	Params:
		client_socket: socket socket of connecting client
		client_addr: address address of connection client
		server_info: dict containing information about server
		lock: threading.Lock() used when editing kill_service_value
	"""

	running = True
	respond = True		#used to signal whether a response should be sent
	while running:

		client_msg = client_socket.recv(65536)
		response = ""

		#start of command logic
		if client_msg.startswith("HELO ", 0, 5):
			response = process_helo_command(server_info, client_msg, client_addr)
			respond = True

		elif client_msg == "KILL_SERVICE\n":
			print("Kill Service Command!!!")		
			with lock:
				global kill_service_value
				kill_service_value = True
				running = False
			respond = False

		else:
			process_unregistered_command(server_info, client_msg)
			respond = False
		
		if respond:
			client_socket.send(response)

	client_socket.close()

def process_helo_command(server_info, msg, client_addr):
	"""
	Handler for "HELO" command.
	Params:
		server_info: dict containing information about the server
		client_addr: address of the client connected
	"""
	response = "%sIP:%s\nPort:%s\nStudent ID:%s\n"%(
		msg, 
		server_info["host"], 
		client_addr["port"],
		server_info["sid"]
	)
	return response

def process_unregistered_command(server_info, msg):
	"""
	Handler for unrecognised commands
	"""
	print("received unregistered command: %s\nDoing nothing."%msg)

if __name__ == '__main__':
    server = tcp_server(int(sys.argv[1]), 5, 2)
    server.serve()



