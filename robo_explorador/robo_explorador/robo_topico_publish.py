#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import random

# Importa a interface que criamos no pacote robo_interfaces
from robo_interfaces.msg import Sensores

class RoboPublish(Node):
    def __init__(self):
        super().__init__('robo_topico_publish')
        # Cria o publicador no tópico 'monitoramento'
        self.publisher_ = self.create_publisher(Sensores, 'monitoramento', 10)
        # Define um timer para publicar os dados a cada 1 segundo
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info("Nó do robô iniciado. Publicando em 'monitoramento'...")

    def timer_callback(self):
        msg = Sensores()
        # Gera valores aleatórios reais entre 1 e 100
        msg.oxigenio = random.uniform(1.0, 100.0)
        msg.temperatura = random.uniform(1.0, 100.0)
        
        # Publica a mensagem
        self.publisher_.publish(msg)
        self.get_logger().info(f"O2: {msg.oxigenio:.1f} | Temp: {msg.temperatura:.1f} C")

def main(args=None):
    rclpy.init(args=args)
    node = RoboPublish()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
