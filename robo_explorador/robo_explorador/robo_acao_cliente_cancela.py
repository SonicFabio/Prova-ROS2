#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

# Importa a interface da Action
from robo_interfaces.action import MoverRobo

class RoboAcaoClienteCancela(Node):
    def __init__(self):
        super().__init__('robo_acao_cliente_cancela')
        self._action_client = ActionClient(self, MoverRobo, 'deslocamento_robo')
        self.goal_handle = None

    def enviar_meta(self, lat, lon, v_lat, v_lon):
        self.get_logger().info('Aguardando o Servidor de Ação...')
        self._action_client.wait_for_server()

        meta_msg = MoverRobo.Goal()
        meta_msg.latitude = lat
        meta_msg.longitude = lon
        meta_msg.vel_latitude = v_lat
        meta_msg.vel_longitude = v_lon

        self.get_logger().info(f'Enviando meta de deslocamento -> Lat: {lat}, Lon: {lon}')
        
        self._send_goal_future = self._action_client.send_goal_async(
            meta_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(f'>> [Feedback] Robô em Lat: {fb.latitude_atual:.2f}, Lon: {fb.longitude_atual:.2f}')

    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.get_logger().info('Meta REJEITADA pelo servidor!')
            return

        self.get_logger().info('Meta ACEITA! Iniciando timer de 5 segundos para cancelar...')
        
        # Aguarda o resultado final (que será forçado pelo cancelamento)
        self._get_result_future = self.goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
        
        # Cria um timer que executará a função cancelar_meta em exatamente 5.0 segundos
        self.timer = self.create_timer(5.0, self.cancelar_meta)

    def cancelar_meta(self):
        self.get_logger().warn('ATENÇÃO: 5 segundos se passaram! Solicitando CANCELAMENTO da ação...')
        self.goal_handle.cancel_goal_async()
        self.timer.cancel() # Para o timer para não ficar chamando o cancelamento repetidas vezes

    def get_result_callback(self, future):
        resultado = future.result().result
        self.get_logger().info(f'AÇÃO ENCERRADA! Distância total percorrida antes do cancelamento: {resultado.distancia_percorrida:.2f}')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    action_client = RoboAcaoClienteCancela()
    
    # Envia uma meta bem distante para garantir que o robô não chegue antes dos 5 segundos
    action_client.enviar_meta(50.0, 50.0, 1.0, 1.0)
    
    rclpy.spin(action_client)

if __name__ == '__main__':
    main()
