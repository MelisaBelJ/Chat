from multiprocessing.connection import Listener
from multiprocessing import Process, Lock, Value
from multiprocessing.connection import AuthenticationError
from time import time
import sys

class Servidor():
    def __init__(self, ip_address):
        self.clientes = {}
        self.enChat = {}
        self.lock = Lock()
        
        with  Listener(address=(ip_address, 6000), authkey=b'secret password') as listener:
            while True:
                try:
                    conn = listener.accept()
                    print ('Conectado con', listener.last_accepted)
                    usuario = conn.recv()
                    p = Process(target=self.serve_client, args=(conn, usuario))
                    with self.lock:
                        self.clientes[usuario] = conn
                        self.enChat[usuario] = Value('i', 0)
                    p.start()
                except AuthenticationError:
                    print ('Connection refused, incorrect password')
        
    def serve_client(self, conn, pid):
        try:
            m = conn.recv()
            with self.lock:
                if self.enChat[pid].value == 0:
                    if m in self.clientes:
                        mensaje = f'Conectando {pid} con {m}'
                        self.enChat[pid].value = 1
                        self.enChat[m].value = 1
                        self.clientes[m].send('')
                        self.clientes[m].send('')
                        Chat([self.clientes[pid],self.clientes[m]],[pid, m])
                    else:
                        mensaje = f'No existe un usuario con nombre: {m}'
                    print(mensaje)
        except EOFError:
            print ('Conexion cortada')     
            conn.close()
        
    

class Chat():
    def __init__(self, conns, usernames):
        self.lock = Lock()
        NOMBRE = ''
        self.continua = {}
        self.conexiones = {}
        for i in range(len(conns)):
            self.continua[usernames[i]] = Value('i', 1)
            self.conexiones[usernames[i]] = conns[i] 
            NOMBRE += f' {usernames[i]}'
        with self.lock:
            for u in usernames:
                self.conexiones[u].send('En chat')
                self.conexiones[u].send(f'{NOMBRE} \n')
                Process(target=self.connect_client, args=(u,)).start()
        
    def connect_client(self, username):
        m, conn = '', self.conexiones[username]
        while self.continua[username].value == 1:
            try:
                m = conn.recv()
                with self.lock:
                    for user in self.conexiones:
                        if user != username and self.continua[user].value == 1:
                            self.conexiones[user].send(username)
                            if m != 'adios':
                                self.conexiones[user].send(m)
                            else:
                                self.conexiones[user].send(f'Ha salido')
                    self.continua[username].value = m != 'adios'
            except EOFError:
                print ('Conexion cortada')
                break  
        print(username, 'left')
        conn.send('')
        conn.send('adios')
        conn.close()

if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    Servidor(ip_address)
