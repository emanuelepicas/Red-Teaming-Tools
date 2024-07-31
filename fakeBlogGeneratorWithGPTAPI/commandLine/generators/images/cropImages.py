from io import BytesIO
from PIL import Image
import base64


def crop_image(image_data):
    # Load the image from binary data
    image = Image.open(BytesIO(image_data))

    # Define the crop box coordinates (left, upper, right, lower)
    crop_box = (220, 200, 820, 950)

    # Crop the image
    cropped_image = image.crop(crop_box)

    print('The image is croped')

    cropped_image_binary = BytesIO()
    cropped_image.save(cropped_image_binary, format='JPEG')
    cropped_image_binary.seek(0)
    image_datas = cropped_image_binary.read()

    cropped_image_final = base64.b64encode(image_datas)

    return(cropped_image_final)