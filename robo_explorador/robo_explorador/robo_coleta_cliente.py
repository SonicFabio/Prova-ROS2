#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import random

# Importa a interface do serviço que criamos
from robo_interfaces.srv import Coleta

class RoboColetaCliente(Node):
    def __init__(self):
        super().__init__('robo_coleta_cliente')
        # Cria o cliente para o serviço chamado 'coleta_material'
        self.client = self.create_client(Coleta, 'coleta_material')
        
        # Aguarda até que o servidor do serviço esteja online
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Serviço de coleta não está disponível, aguardando...')
        
        self.req = Coleta.Request()

    def enviar_requisicao(self):
        # Gera a profundidade aleatória entre 0.1 e 0.5
        self.req.profundidade = random.uniform(0.1, 0.5)
        self.get_logger().info(f'Solicitando coleta na profundidade: {self.req.profundidade:.2f}...')
        
        # Envia a requisição de forma assíncrona
        self.future = self.client.call_async(self.req)
        # Acopla uma função para rodar quando a resposta chegar
        rclpy.spin_until_future_complete(self, self.future)
        
        return self.future.result()

def main(args=None):
    rclpy.init(args=args)
    
    cliente = RoboColetaCliente()
    resposta = cliente.enviar_requisicao()
    
    # Avalia a resposta do servidor para dizer se foi bem sucedida
    if resposta is not None:
        if resposta.sucesso:
            cliente.get_logger().info('Resultado: Coleta BEM SUCEDIDA!')
        else:
            cliente.get_logger().info('Resultado: Falha na coleta.')
    else:
        cliente.get_logger().error('Falha ao chamar o serviço.')

    cliente.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
