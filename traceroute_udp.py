import socket
import time

# Função para criação do soquete que irá receber a mensagem ICMP echo reply
def create_receiver(port):
    icmp = socket.getprotobyname('icmp')
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    # Definir o tempo de espera da resposta para 3 segundos
    s.settimeout(3) 
    
    try:
        s.bind(('', port))

    except socket.error as e:
        raise IOError('Não foi possível vincular o socket receiver: {}'.format(e))

    return s

# Função para criação do soquete que irá enviar a mensagem ICMP echo request
def create_sender(ttl):
    udp = socket.getprotobyname('udp')
    
    # Mensagem será empacotada em um segmento UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp) 
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

    return s

# Função principal para executar o código do traceroute
def run():
    max_ttl = int(input('Digite o TTL máximo: '))
    dest = input('Digite o endereço URL de destino: ')
    port = 33434
    ttl = 1
    
    try:
        # Tradução do endereço URL
        dest_ip = socket.gethostbyname(dest) 

    except socket.error as e:
        raise IOError('Não foi possível traduzir este endereço {}: {}', dest, e)

    # Formatação do texto em tela        
    text = '\nTraçando a rota para {} ({}) - TTL máximo de {}\n'.format(dest, dest_ip, max_ttl)
    print(text)
    print('{:<10} {:<20} {}'.format('TTL', 'TIME (ms)', 'IP ADDRESS\n'))

    # Loop principal da função 
    while True:

        # Criação dos soquetes
        receiver = create_receiver(port)
        sender = create_sender(ttl)

        # Envio da mensagem sem carga útil para o IP de destino
        sender.sendto(b'', (dest, port)) 
        
        # Variáveis para armazenar o nome e endereço IP do roteador ou host
        addr_ip = None
        addr_name = None

        # Marcar o tempo que a mensagem foi enviada para cálculo do tempo de resposta
        start_time = round(time.time()*1000) 

        try:
            # Armazenar a mensagem de resposta nas variáveis
            data, addr = receiver.recvfrom(1024) 

            # Marcar o tempo que a mensagem foi recebida para cálculo do tempo de resposta
            receive_time = round(time.time()*1000)
 
            addr_ip = addr [0]

            try:
                addr_name = socket.gethostbyaddr(addr_ip)[0]
            except socket.error:
                addr_name = addr_ip

        # Dar continuidade ao código se a mensagem exceder o tempo de 3 segundos definido (Evita ficar esperando por muito tempo a resposta) 
        except socket.timeout:
            pass

        # Fechar os soquetes
        finally:
            receiver.close()
            sender.close()

        # Mensagem impressa na tela com o ttl, tempo de resposta, endereço e nome (quando houver) do roteador ou host
        # Só irá imprimir se o addr_ip for diferente de None
        if addr_ip:
            if addr_name == addr_ip:
                print('{:<10} {:<20} {}'.format(ttl, str('{} ms').format((receive_time - start_time)), addr_ip))

            else:
                print('{:<10} {:<20} {} ({})'.format(ttl, str('{} ms').format((receive_time - start_time)), addr_name, addr_ip))

        else:
            print('{:<10} * Esgotado o tempo limite do pedido'.format(ttl))

        # Incremento para passar para o próximo roteador ou host
        ttl += 1

        # Se o endereço recebido na mensagem for o mesmo do destino quebra o loop while
        if addr_ip == dest_ip:
            print('Rota traçada com sucesso')
            break
        
        # Se o TTL máximo for estourado quebra o loop while
        if ttl > max_ttl:
            print('Não foi possível alcançar o host de destino')
            break

#Chamar a função principal do código
if __name__ == '__main__':
    run()    