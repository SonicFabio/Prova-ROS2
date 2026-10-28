#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

# Importa a interface da mensagem
from robo_interfaces.msg import Sensores

class RoboSubscriber(Node):
    def __init__(self):
        super().__init__('robo_topico_subscriber')
        # Inscreve-se no tópico 'monitoramento'
        self.subscription = self.create_subscription(
            Sensores,
            'monitoramento',
            self.listener_callback,
            10)
        self.subscription  # previne aviso de variável não utilizada
        self.get_logger().info("Estação Base iniciada. Escutando o robô...")

    def listener_callback(self, msg):
        # Aplica a lógica da Questão 4
        if 10 <= msg.temperatura <= 40 and msg.oxigenio > 80:
            status = "Safe"
        else:
            status = "Not Safe"
            
        self.get_logger().info(f"O2: {msg.oxigenio:.1f} | Temp: {msg.temperatura:.1f} C => Ambiente: {status}")

def main(args=None):
    rclpy.init(args=args)
    node = RoboSubscriber()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
