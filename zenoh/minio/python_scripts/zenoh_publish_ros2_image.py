import rclpy
from sensor_msgs.msg import Image
import zenoh

def image_callback(msg):
    # Extract image data from ROS2 message
    image_data = msg.data

    # Publish the image data over Zenoh
    topic = "image_data"
    try:
        pub = session.declare_publisher(topic)
        pub.put(image_data)
    except zenoh.ZenohError as e:
        print(f"Error while publishing image data: {e}")

def main(args=None):
    rclpy.init(args=args)

    # Initialize Zenoh session
    session = zenoh.open()

    node = rclpy.create_node('image_subscriber')

    # Subscribe to the ROS2 image topic
    image_subscription = node.create_subscription(Image, '/limo/depth_camera_link/image_raw', image_callback, 10)
    image_subscription  # prevent unused variable warning

    print("Subscribed to ROS2 topic '/limo/depth_camera_link/image_raw'")

    rclpy.spin(node)

    # Close Zenoh session
    session.close()
    rclpy.shutdown()


if __name__ == '__main__':
    main()