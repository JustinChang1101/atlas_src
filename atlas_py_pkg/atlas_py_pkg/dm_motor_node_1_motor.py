import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64
import serial
import time

from .DM_CAN import MotorControl, Motor, DM_Motor_Type, Control_Type

class DMMotorNode(Node):
    def __init__(self):
        super().__init__('dm_motor_node')
        
        # 初始化 Publisher (發布關節狀態至 joint_states 頻道)
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # 初始化 Subscriber (訂閱 joint_commands 頻道)
        self.command_sub = self.create_subscription(Float64, 'joint_commands', 
                           self.command_callback, 10)
        
        # 設定硬體通訊 (樹莓派上為'/dev/ttyACM0')
        self.get_logger().info("Connecting to USB2CAN...")
        try:
            self.serial_device = serial.Serial('/dev/ttyACM0', 921600, timeout=0.5)
            self.motor_control = MotorControl(self.serial_device)
            
            # 定義馬達 (以 ID 0x01 為例)
            self.motor1 = Motor(DM_Motor_Type.DM4310, 0x01, 0x11)
            self.motor_control.addMotor(self.motor1)
            
            # 喚醒並切換到 POS_VEL 模式
            self.motor_control.enable(self.motor1)
            time.sleep(1)
            if self.motor_control.switchControlMode(self.motor1, Control_Type.POS_VEL):
                print("Successfully changed to POS_VEL mode!")
            
        except Exception as e:
            self.get_logger().error(f"Error: {e}")
            return

        # 建立計時器，每 0.1 秒讀取並發布一次狀態 (10Hz)
        self.timer = self.create_timer(0.1, self.publish_joint_state)
    
    # 新增收到指令時的觸發動作
    def command_callback(self, msg):
        target_position = msg.data
        # 參數依序為：(馬達物件, 目標位置rad, 目標極限速度rad/s)
        # 我們先把安全極速設定在 2.0 rad/s
        self.motor_control.control_Pos_Vel(self.motor1, target_position, 2.0)
        self.get_logger().info(f"收到指令！正移動至：{target_position:.2f} 弧度")

    def publish_joint_state(self):
        # 更新馬達狀態
        self.motor_control.refresh_motor_status(self.motor1)
        
        # 打包成 ROS 2 的 JointState 訊息
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1'] # 你的馬達名稱
        msg.position = [float(self.motor1.getPosition())]
        msg.velocity = [float(self.motor1.getVelocity())]
        msg.effort = [float(self.motor1.getTorque())]
        
        # 發布訊息
        self.joint_pub.publish(msg)

    def destroy_node(self):
        # 節點關閉時的安全機制
        self.get_logger().info("Shutting down motors...")
        self.motor_control.disable(self.motor1)
        self.serial_device.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = DMMotorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
