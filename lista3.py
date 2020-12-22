######################################
# Lista 3 - Sistemas Operacionais
######################################
import threading 
import time
import socket
import os
#
HOST = ''              # '' significa endereco local
PORT = 5000       # porta que o servidor aguarda conexoes
#
# cria um socket TCP/IP tipo servidor
serverSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
orig = (HOST, PORT)
serverSoc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serverSoc.bind(orig)
serverSoc.listen(1)    # 1: tamanho maximo da fila de conexões pendentes
#
# define um buffer global para comunicacao inter-threads
requests = []

# mutex (locker) e variavel de condicao para proteger o buffer
# Python combina mutex e variavel de condicao na mesma estrutura Condition
condvar = threading.Condition()

# define uma thread que ira receber requisicoes
def threadMestre():
    while True:
        # recebe uma requisicao
        req = input("Digite uma requisicao: ")
        # armazena a requisicao
        # REGIAO CRITICA: INICIO
        condvar.acquire()
        requests.append(req)
        # sinalize uma thread trabalhadora
        condvar.notify()
        condvar.release()
        # REGIAO CRITICA: FIM
    
# define thread trabalhadora
def threadTrab(id):
    ident = id
    while True:
        # acessa uma requisicao
        # REGIAO CRITICA: INICIO
        condvar.acquire()       
        if len(requests) == 0:
            condvar.wait()      # buffer vazio: bloqueia
        # lista nao vazia
        req = requests[0]
        requests.pop(0)         # remove primeiro elemento
        condvar.release()       # nao esqueca de liberar o mutex
        # REGIAO CRITICA: FIM
        # trabalha na requisicao
        time.sleep(3)
        print("Processamento da requisicao {} concluida pela thread {}"\
              .format(req, ident))

# programa principal
if __name__ == "__main__":
    # cria uma thread mestre
    thm = threading.Thread(target=threadMestre, args=())
    thm.start()
    # cria 3 thread trabalhadoras
    tht1 = threading.Thread(target=threadTrab, args=('T1',))
    tht1.start()
    tht2 = threading.Thread(target=threadTrab, args=('T2',))
    tht2.start()
    tht3 = threading.Thread(target=threadTrab, args=('T3',))
    tht3.start()

    # aguarda thread mestre terminar para sair
    thm.join()
# aceita e processa requisicoes
while True:
    connection, cliente = serverSoc.accept()
    print('\n\nConectado por {}'.format(cliente))

    # processa a requisicao
    # a partir daqui esta tarefa seria executada por uma thread trabalhadora

    req = connection.recv(1024)     # le 1024 bytes do socket
    if not req:     # cliente fechou a conexao
        connection.close()
        continue
    req = req.decode('ascii')
    print(req)
    reqLines = req.split('\r\n')
    print('Primeira Linha: {}'.format(reqLines[0]))
    reqParts = reqLines[0].split()
    if reqParts[1] == '/':
        resource = './web/index.html'
    else:
        resource = './web' + reqParts[1]
    print('Recurso requisitado: {}'.format(resource))
    # evia o recurso ao cliente
    try:     # envia recurso
        file = open(resource, 'r')
        size = str(os.path.getsize(resource))
        # cabecalho de retorno
        cab = 'HTTP/1.1 200 OK\r\n'
        # content-type depende da extensao do recurso requisitado:
        # text/html, text/plain, image/jpeg, image/png, image/gif, etc.
        cab = cab + 'Content-Type: text/html\r\n'
        cab = cab + 'Content-Length: ' + size + '\r\n\r\n'
        connection.send(cab.encode('utf-8'))
        # conteudo de retorno
        connection.send(bytes(file.read(), 'utf-8'))
        file.close()
    except:     # recurso nao existe
        line = 'HTTP/1.1 404 Not Found\r\n\r\n'
        connection.send(line.encode('utf-8'))
    print('Finalizando conexao.')
    connection.close()