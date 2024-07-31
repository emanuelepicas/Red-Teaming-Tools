import base64
import shutil
from generators.images.cropImages import crop_image
from utils.ageSplit import what_is_the_range
import requests
import sys
sys.path.append('../../')

def get_image(gender_, age_):
    '''
    Function for retriving the profile images for the author from website https://this-person-does-not-exist.com/
    This is not a direct call because there is a small implementation interface on the website 
    Mainly are two calls, the for having an image based on selected parameter and the second for retriving the image itself
    '''
    gender_final = ''
    gender = ['all', 'male', 'female']
    if (str(gender_).lower() == 'male'):
        gender_final = gender[1]
    else:
        gender_final = gender[2]
    age = what_is_the_range(age_)

    # etnicity = ['all', 'asian', 'black', 'white', 'indian', 'middle-eastern', 'latino_hispanic']
    try:
        url = f"https://this-person-does-not-exist.com/new?gender={gender_final}&age={age}&etnic=all"
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            # Extract the "src" field from the JSON data
            src_field = data.get("src")

            if src_field is not None:
                final_url_for_the_image = f'https://this-person-does-not-exist.com{src_field}'
                print('this is the final url: ' + final_url_for_the_image)
                image = requests.get(final_url_for_the_image)
                final_image = crop_image(image.content)
                # print('sono qui ------------------>')
                return final_image
            else:
                print("The 'src' field was not found in the JSON response.")
                return None
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return None

    except:
        return None


def getImageArticle(api_key_ninjas):
    '''
    Function for retriving the images for the articles from the service API ninjas
    Documentation link: https://api-ninjas.com/api/randomimage 
    Free service, availability 50000 calls per month
    '''
    category = 'technology'
    # For now it is technology
    # Other possible values: nature, city, technology, food, still_life, abstract, wildlife.
    api_url = 'https://api.api-ninjas.com/v1/randomimage?category={}&width=1200&height=1200'.format(
        category)
    response = requests.get(api_url, headers={
                            'X-Api-Key': api_key_ninjas, 'Accept': 'image/jpg'}, stream=True)
    if response.status_code == requests.codes.ok:
        image_content = response.content
        base64_image = base64.b64encode(
            image_content)  # Convert bytes to string
        return base64_image
    else:
        print("Error retriving image article:",
              response.status_code, response.text)
        empty_image = b'00'
        return empty_image


def getBannerImage(template_number, api_key_ninjas):
    '''
    Function for retriving the banner image from the service API ninjas
    Documentation link: https://api-ninjas.com/api/randomimage 

    Free service, availability 50000 calls per month
    '''
    print("calling the API for the banner iamge")
    api_url = 'https://api.api-ninjas.com/v1/randomimage?category=abstract&width=1600&height=1067'
    response = requests.get(api_url, headers={
                            'X-Api-Key': api_key_ninjas, 'Accept': 'image/jpg'}, stream=True)
    if response.status_code == requests.codes.ok:
        with open('base_templates/template%s/static/images/bannerImage.png' % template_number, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
    else:
        print("Error:", response.status_code, response.text)
