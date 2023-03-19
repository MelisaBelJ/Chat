from multiprocessing.connection import Client
import sys
from multiprocessing import Process, Lock, Value

class Cliente():
    def __init__(self, ip_address):
        self.conectaCon(ip_address)

    def conectaCon(self, ip_address):
        print ('Intentando conectar')
        self.conn = Client(address=(ip_address, 6000), authkey=b'secret password')
        self.continua = Value('i', 1)
        usuario = input('Nombre de usuario: ')
        self.conn.send(usuario)
        p = Process(target=self.recibeMensajes, args=())
        p.start()
        self.enviaMensajes()
        p.join()
        self.conn.close()
                
    def recibeMensajes(self):
        while self.continua.value==1:
            self.desplazaTerminal(1, 36)
            usuario = self.conn.recv()
            message = self.conn.recv()
            if usuario != '':
                print(f'{usuario}:', message, '\n')
            else:
                self.conn.send('')
            self.continua.value = int(message != 'adios')
        print('Fuera')
        self.conn.send('adios')
        
            
    def enviaMensajes(self):
        while self.continua.value == 1:
            message = input('')
            self.desplazaTerminal(2, 37)
            print('Yo:', message, '\n')
            self.conn.send(message)
            self.continua.value = int(message != 'adios')
            
    def desplazaTerminal(self, n, cod):
        for i in range(n):
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            
        sys.stdout.write(f'\033[{cod}m')
                
if __name__=="__main__":
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    Cliente(ip_address)
