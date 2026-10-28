#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
import time
import math

# Importa a interface da Action
from robo_interfaces.action import MoverRobo

class RoboAcaoServidor(Node):
    def __init__(self):
        super().__init__('robo_acao_servidor')
        # Inicia o Servidor de Ação no endpoint 'deslocamento_robo'
        self._action_server = ActionServer(
            self,
            MoverRobo,
            'deslocamento_robo',
            self.execute_callback)
        
        # Posição inicial simulada do robô
        self.lat_atual = 0.0
        self.lon_atual = 0.0
        self.get_logger().info('Servidor de Ação pronto. Aguardando metas de deslocamento...')

    def execute_callback(self, goal_handle):
        self.get_logger().info('Nova meta de deslocamento recebida!')
        meta = goal_handle.request
        
        # Requisito: Se a localização for igual a atual, aborta (só tem sucesso se for diferente)
        if self.lat_atual == meta.latitude and self.lon_atual == meta.longitude:
            self.get_logger().warn('O robô já está na localização solicitada.')
            goal_handle.abort()
            resultado = MoverRobo.Result()
            resultado.distancia_percorrida = 0.0
            return resultado

        lat_inicial = self.lat_atual
        lon_inicial = self.lon_atual
        feedback_msg = MoverRobo.Feedback()
        
        # Loop de deslocamento do robô
        while True:
            # Verifica se o cliente solicitou cancelamento no meio do caminho (Questão 11)
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Deslocamento CANCELADO pelo cliente.')
                resultado = MoverRobo.Result()
                # Retorna a distância percorrida até o momento do cancelamento
                resultado.distancia_percorrida = math.sqrt((self.lat_atual - lat_inicial)**2 + (self.lon_atual - lon_inicial)**2)
                return resultado

            dist_lat = meta.latitude - self.lat_atual
            dist_lon = meta.longitude - self.lon_atual
            dist_restante = math.sqrt(dist_lat**2 + dist_lon**2)
            
            # Se chegou muito perto (margem de tolerância), encerra o loop
            if dist_restante < 0.5: 
                self.lat_atual = meta.latitude
                self.lon_atual = meta.longitude
                break
            
            # Move o robô na direção do alvo com as velocidades informadas
            passo_lat = meta.vel_latitude if dist_lat > 0 else -meta.vel_latitude
            passo_lon = meta.vel_longitude if dist_lon > 0 else -meta.vel_longitude
            
            # Garante que ele não ultrapasse o alvo
            if abs(dist_lat) < abs(passo_lat): passo_lat = dist_lat
            if abs(dist_lon) < abs(passo_lon): passo_lon = dist_lon
            
            self.lat_atual += passo_lat
            self.lon_atual += passo_lon
            
            # Publica o feedback a cada 1 segundo (Questão 9)
            feedback_msg.latitude_atual = self.lat_atual
            feedback_msg.longitude_atual = self.lon_atual
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Feedback -> Lat: {self.lat_atual:.2f}, Lon: {self.lon_atual:.2f}')
            
            time.sleep(1.0)
            
        # Declara a ação como concluída com sucesso
        goal_handle.succeed()
        resultado = MoverRobo.Result()
        resultado.distancia_percorrida = math.sqrt((self.lat_atual - lat_inicial)**2 + (self.lon_atual - lon_inicial)**2)
        
        self.get_logger().info(f'Meta CONCLUÍDA! Distância total: {resultado.distancia_percorrida:.2f}')
        return resultado

def main(args=None):
    rclpy.init(args=args)
    node = RoboAcaoServidor()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
