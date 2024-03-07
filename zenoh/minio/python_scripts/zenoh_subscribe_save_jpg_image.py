import zenoh
import time
import base64
from PIL import Image
import io
import time
from datetime import datetime

# Define the topic where the image data will be published
topic = "vista/image_data"

# Callback function to handle received image data
def handle_image_data(data):
    try:
        # Extract image data from Zenoh message
        image_data = data.payload

        # Convert image data to base64 string
        image_data_base64 = base64.b64decode(image_data)

        # Attempt to open the image with PIL
        image = Image.open(io.BytesIO(image_data_base64))

        timestamp = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

        # Save the image to file
        image_filename = f"received_image_{timestamp}.jpg"
        image.save(image_filename)
        print(f"Image saved to {image_filename}")
    except Exception as e:
        print(f"Error while decoding image: {e}")

if __name__ == "__main__":
    session = zenoh.open()
    sub = session.declare_subscriber(topic, handle_image_data)
    time.sleep(60)  # Keep the program running for 60 seconds
