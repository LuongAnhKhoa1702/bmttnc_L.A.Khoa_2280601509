import sys
from PIL import Image

def decode_image(encoded_image_path):
    img = Image.open(encoded_image_path)
    width, height = img.size
    binary_message = ""

    # Iterate through pixels
    for row in range(height):
        for col in range(width):
            # Ensure pixel is a list to allow modification if needed, though for decoding it's not strictly necessary
            pixel = list(img.getpixel((col, row)))

            # Iterate through color channels (RGB)
            for color_channel in range(3):
                # Extract the least significant bit
                binary_message += format(pixel[color_channel], '08b')[-1]

                # Check for the termination sequence '1111111111111110'
                # We need to check a window of 16 bits to find the terminator
                # and ensure we don't go out of bounds of the collected binary_message
                if len(binary_message) >= 16 and binary_message[-16:] == '1111111111111110':
                    # Remove the termination sequence
                    binary_message = binary_message[:-16]
                    # Convert binary string to characters
                    message = ""
                    try:
                        # Iterate through the binary message in chunks of 8 bits (1 byte)
                        for i in range(0, len(binary_message), 8):
                            byte = binary_message[i:i+8]
                            # Convert 8-bit binary string to an integer, then to a character
                            message += chr(int(byte, 2))
                    except ValueError:
                        # Handle cases where the binary string might not be a valid byte
                        return "Could not decode message. Possible corruption or invalid image."
                    return message

    return "No hidden message found or message not terminated correctly."

# The main function should be at the same indentation level as decode_image
def main():
    if len(sys.argv) != 2:
        print("Usage: python decrypt.py <encoded_image_path>")
        return

    encoded_image_path = sys.argv[1]
    decoded_message = decode_image(encoded_image_path)
    print("Decoded message:", decoded_message)

if __name__ == "__main__":
    main()