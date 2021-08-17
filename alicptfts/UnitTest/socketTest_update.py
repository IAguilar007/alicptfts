import socket, traceback
import threading
import sys, time
import multiprocessing


def client_send(clientMessage = 'Hello!'):
    HOST = '127.0.0.1'
    PORT = 8000
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect((HOST, PORT))
    print('client send message: %s' % clientMessage)
    client.sendall(clientMessage.encode())


    serverMessage = str(client.recv(1024), encoding='utf-8')
    print('Client received message:', serverMessage)
    client.close()

def server():
    HOST = '127.0.0.1'
    PORT = 8000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    print('Status: server is listening\n')

    try:
        while True:
            '''
            try:
                conn, addr = server.accept()
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc()
                #continue
            '''

            conn, addr = server.accept()
            print('Connected by', addr)
            clientMessage = str(conn.recv(1024), encoding='utf-8')

            print('Server received message:', clientMessage)

            serverMessage = 'I got it'
            print('server send message: %s' % serverMessage)
            conn.sendall(serverMessage.encode())
            conn.close()

    except KeyboardInterrupt:
        print('Server closing')
        server.close()




if __name__ == '__main__':
    #event = threading.Event()
    job_server = threading.Thread(target=server)
    job_client = threading.Thread(target=client_send)
    #job_server = multiprocessing.Process(target=server)
    #job_client = multiprocessing.Process(target=client_send)
    #job_server.daemon = True
    job_server.start()
    job_client.start()
    '''
    try:
        job_server.start()
        job_client.start()

    except KeyboardInterrupt:
        print('Terminate program')
        #if job_server.is_alive() : job_server.join()
        #if job_client.is_alive() : job_client.join()
        #job_client.terminate()
        #job_server.terminate()
        sys.exit(1)
    #event.set()
    #client_send()
    '''
