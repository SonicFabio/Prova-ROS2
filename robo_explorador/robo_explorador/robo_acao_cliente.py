#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

# Importa a interface da Action
from robo_interfaces.action import MoverRobo

class RoboAcaoCliente(Node):
    def __init__(self):
        super().__init__('robo_acao_cliente')
        # Cria o cliente de ação
        self._action_client = ActionClient(self, MoverRobo, 'deslocamento_robo')

    def enviar_meta(self, lat, lon, v_lat, v_lon):
        self.get_logger().info('Aguardando o Servidor de Ação...')
        self._action_client.wait_for_server()

        meta_msg = MoverRobo.Goal()
        meta_msg.latitude = lat
        meta_msg.longitude = lon
        meta_msg.vel_latitude = v_lat
        meta_msg.vel_longitude = v_lon

        self.get_logger().info(f'Enviando meta de deslocamento -> Lat: {lat}, Lon: {lon}')
        
        # Envia a meta e configura a função de callback para o feedback
        self._send_goal_future = self._action_client.send_goal_async(
            meta_msg,
            feedback_callback=self.feedback_callback
        )
        # Configura a função para quando o servidor aceitar a meta
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Meta foi REJEITADA pelo servidor!')
            return

        self.get_logger().info('Meta ACEITA! Aguardando o deslocamento...')
        # Fica aguardando o resultado final
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        # Imprime os dados contínuos de localização recebidos do servidor
        fb = feedback_msg.feedback
        self.get_logger().info(f'>> [Feedback Recebido] Robô em Lat: {fb.latitude_atual:.2f}, Lon: {fb.longitude_atual:.2f}')

    def get_result_callback(self, future):
        # Imprime a distância percorrida ao final da ação
        resultado = future.result().result
        self.get_logger().info(f'DESLOCAMENTO CONCLUÍDO! Distância percorrida: {resultado.distancia_percorrida:.2f}')
        
        # Encerra o nó do ROS2 após receber o resultado final
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = RoboAcaoCliente()
    
    # Envia a ordem para ir para a Latitude 10, Longitude 5, com velocidade 2.0 por segundo
    action_client.enviar_meta(10.0, 5.0, 2.0, 2.0)
    
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()
