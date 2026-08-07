import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray  # 升級成支援多關節傳遞的陣列型態
import serial
import time

from .DM_CAN import MotorControl, Motor, DM_Motor_Type, Control_Type

class DMMotorNode(Node):
    def __init__(self):
        super().__init__('dm_motor_node')
        
        # 狀態發布器與指令訂閱器
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.command_sub = self.create_subscription(
            Float64MultiArray,
            'joint_commands',
            self.command_callback,
            10
        )
        
        self.get_logger().info("Connecting to Daedalus USB-to-CAN module for 3-DOF Arm...")
        try:
            self.serial_device = serial.Serial('/dev/ttyACM0', 921600, timeout=0.5)
            self.motor_control = MotorControl(self.serial_device)
            
            # 初始化三顆不同 ID 的 DM4310 馬達
            self.motor1 = Motor(DM_Motor_Type.DM4310, 0x01, 0x11)
            self.motor2 = Motor(DM_Motor_Type.DM4310, 0x02, 0x12)
            self.motor3 = Motor(DM_Motor_Type.DM4310, 0x03, 0x13)
            
            # 將三顆馬達加入控制器管理
            self.motor_control.addMotor(self.motor1)
            self.motor_control.addMotor(self.motor2)
            self.motor_control.addMotor(self.motor3)
            
            # 將啟動位置設為0 rad
            self.motor_control.set_zero_position(self.motor1)
            self.motor_control.set_zero_position(self.motor2)
            self.motor_control.set_zero_position(self.motor3)

            # 依序致能 (Enable)
            self.motor_control.enable(self.motor1)
            self.motor_control.enable(self.motor2)
            self.motor_control.enable(self.motor3)
            time.sleep(1)
            
            # 全部切換為 POS_VEL（位置速度）模式
            self.motor_control.switchControlMode(self.motor1, Control_Type.POS_VEL)
            self.motor_control.switchControlMode(self.motor2, Control_Type.POS_VEL)
            self.motor_control.switchControlMode(self.motor3, Control_Type.POS_VEL)
            
            self.get_logger().info("All 3 motors initialized and enabled successfully!")
            
        except Exception as e:
            self.get_logger().error(f"Hardware connection failed: {e}")
            return

        # 定時回報三顆馬達的狀態 (10Hz)
        self.timer = self.create_timer(0.1, self.publish_joint_state)

    def command_callback(self, msg):
        """接收包含三個角度的陣列指令"""
        if len(msg.data) >= 3:
            target1 = msg.data[0]
            target2 = msg.data[1]
            target3 = msg.data[2]
            
            # 同步下達位置指令給三顆馬達
            self.motor_control.control_Pos_Vel(self.motor1, target1, 2.0)
            self.motor_control.control_Pos_Vel(self.motor2, target2, 2.0)
            self.motor_control.control_Pos_Vel(self.motor3, target3, 2.0)
            
            self.get_logger().info(f"Targets -> J1: {target1:.2f}, J2: {target2:.2f}, J3: {target3:.2f}")

    def publish_joint_state(self):
        """更新並廣播三顆馬達的狀態"""
        self.motor_control.refresh_motor_status(self.motor1)
        self.motor_control.refresh_motor_status(self.motor2)
        self.motor_control.refresh_motor_status(self.motor3)
        
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = ['joint_1', 'joint_2', 'joint_3']
        
        msg.position = [
            float(self.motor1.getPosition()),
            float(self.motor2.getPosition()),
            float(self.motor3.getPosition())
        ]
        msg.velocity = [
            float(self.motor1.getVelocity()),
            float(self.motor2.getVelocity()),
            float(self.motor3.getVelocity())
        ]
        msg.effort = [
            float(self.motor1.getTorque()),
            float(self.motor2.getTorque()),
            float(self.motor3.getTorque())
        ]
        
        self.joint_pub.publish(msg)

    def destroy_node(self):
        self.get_logger().info("Disabling all motors...")
        self.motor_control.disable(self.motor1)
        self.motor_control.disable(self.motor2)
        self.motor_control.disable(self.motor3)
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
