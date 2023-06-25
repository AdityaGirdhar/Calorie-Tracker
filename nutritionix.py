import requests
import os
from dotenv import load_dotenv
load_dotenv()

def get_calories(food_name):
    api_key = os.getenv('NUTRITIONIX_API_KEY')
    api_endpoint = 'https://trackapi.nutritionix.com/v2/search/instant'

    # Set the request headers
    headers = {
        'Content-Type': 'application/json',
        'x-app-id': '29d1443f',
        'x-app-key': api_key
    }

    # Set the request payload
    payload = {
        'query': food_name,
        'detailed': True
    }

    # Send the POST request to the API
    response = requests.post(api_endpoint, headers=headers, json=payload)

    # Parse the response JSON and extract the calorie data
    data = response.json()
    if 'common' in data and len(data['common']) > 0:
        item = data['branded'][0]
        food_name = item['food_name']
        calories = item['nf_calories']
        return food_name, calories
    else:
        return None, None
    
if __name__ == '__main__':
	str = input('Enter food name: ')
	food_name, calories = get_calories(str)
	print(food_name, calories)