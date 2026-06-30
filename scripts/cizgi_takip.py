#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class CizgiTakipNode(Node):
    def __init__(self):
        super().__init__('cizgi_takip_node')
        
        # Kameradan görüntü dinleme aboneliği
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.im_callback, 10)
            
        # Motorlara otonom hız komutu gönderme yayını
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.bridge = CvBridge()
        self.get_logger().info("Otonom Çizgi Takip Düğümü Başlatıldı!")

    def im_callback(self, msg):
        # ROS 2 görüntüsünü OpenCV formatına çevir
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # 1. Görüntü İşleme: ROI (Sadece yerdeki çizgiye odaklan)
        h, w, _ = frame.shape
        roi = frame[int(h*0.7):h, 0:w] # Alt %30'luk kısmı al
        
        # 2. Gri tona çevir ve eşikleme yap (Siyah/Beyaz şerit için)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY) # Beyaz çizgiyi yakala
        
        # 3. Çizginin Merkezini Bul (Moments)
        M = cv2.moments(mask)
        twist = Twist()
        
        if M['m00'] > 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            
            # Robotun merkezinden ne kadar saptık? (Hata payı)
            robot_merkez = w / 2
            hata = robot_merkez - cx
            
            # basit bir P (Proportional) kontrolör ile otonom dönüş hızı üret
            twist.linear.x = 0.2  # Sabit ileri hız (m/s)
            twist.angular.z = float(hata) / 100.0 # Sapmaya göre sağa/sola dön
            
            # Ekrana çizgiyi çizdir (Görsel doğrulama için)
            cv2.circle(roi, (cx, cy), 5, (0, 0, 255), -1)
        else:
            # Çizgi kaybolduysa robotu durdur ve çizgiyi ara
            twist.linear.x = 0.0
            twist.angular.z = 0.2
            self.get_logger().warn("Çizgi Kayboldu! Aranıyor...")

        # Otonom hız komutunu motorlara gönder!
        self.cmd_pub.publish(twist)
        
        # Canlı işlenen görüntüyü ekranda göster
        cv2.imshow("Robot Kamera Goruntusu", frame)
        cv2.imshow("Maskelenmis Serit", mask)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = CizgiTakipNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
