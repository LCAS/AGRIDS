import zenoh

if __name__ == "__main__":
    # Initialize Zenoh session
    session = zenoh.open()

    # Read the image file
    file_name = "photo001.jpg"
    destination_file = "vineyard001_block001_vinerow001_vine001_"
    
    # Define the topic where the image data will be published + file_name to pass across the file name
    topic = "image_data/" + destination_file + file_name

    try:
        with open(file_name, "rb") as f:
            image_data = f.read()
    except FileNotFoundError:
        print(f"Error: Image file '{file_name}' not found.")
        exit()

    # Define the image name
    image_name = "vine001.jpg"  # Replace this with the actual image file name

    # Declare publisher for the specified topic
    pub = session.declare_publisher(topic)

    # Publish the image data and name on the topic
    print(f"Publishing image data and name on topic '{topic}'...")
    pub.put(image_data)

    # Close Zenoh session
    session.close()