import rclpy
from rclpy.node import Node

class AtlasBrain(Node):
    def __init__(self):
        # 幫這個神經節點取名為 'atlas_brain_node'
        super().__init__('atlas_brain_node')
        # 設定一個計時器，每 1.0 秒呼叫一次 timer_callback
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        # 在終端機印出綠色的訊息
        self.get_logger().info(f'ATLAS 大腦上線測試！系統運作正常，目前心跳數： {self.count}')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    node = AtlasBrain()
    
    try:
        # 讓節點保持運作，持續監聽和發送
        rclpy.spin(node)
    except KeyboardInterrupt:
        # 當你按下 Ctrl+C 時，優雅地關閉
        pass
        
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
