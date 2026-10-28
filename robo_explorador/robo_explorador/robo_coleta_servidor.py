#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import random

from robo_interfaces.srv import Coleta

class RoboColetaServidor(Node):
    def __init__(self):
        super().__init__('robo_coleta_servidor')
        # Cria o serviço no endpoint 'coleta_material'
        self.srv = self.create_service(Coleta, 'coleta_material', self.coleta_callback)
        self.get_logger().info('Servidor de Coleta pronto para receber requisições.')

    def coleta_callback(self, request, response):
        self.get_logger().info(f'Requisição recebida: profundidade de {request.profundidade:.2f} m')
        
        # Sorteia um número de ponto flutuante entre 0.0 e 1.0
        probabilidade = random.random()
        
        # Se for menor ou igual a 0.7, a probabilidade é de 70%
        if probabilidade <= 0.7:
            response.sucesso = True
            self.get_logger().info('Operação de coleta realizada com SUCESSO.')
        else:
            response.sucesso = False
            self.get_logger().warn('FALHA na operação de coleta.')
            
        return response

def main(args=None):
    rclpy.init(args=args)
    node = RoboColetaServidor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
