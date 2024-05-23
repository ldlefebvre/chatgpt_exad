import openai
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Function to generate an image based on a given term
def generate_image(prompt):
    response = openai.Image.create(
        prompt=prompt,
        n=1,  # Number of images to generate per request
        size="1024x1024",
        model="dall-e-3",  # Specify the model to use
        quality="hd"  # You can also use "standard" for standard quality
    )
    return response['data'][0]['url']

# Function to save an image from a URL
def save_image(image_url, save_path):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to retrieve image from {image_url}")

# Main function to generate and save images
def main(term, num_images, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(num_images):
        print(f"Generating image {i+1}/{num_images} for term: {term}")
        image_url = generate_image(term)
        save_path = os.path.join(output_folder, f"{term.replace(' ', '_')}_{i+1}.png")
        save_image(image_url, save_path)
        print(f"Saved image {i+1}/{num_images} to {save_path}")
        time.sleep(1)  # Adding a delay to avoid hitting the rate limit

if __name__ == "__main__":
    term = "extreme sport athlete woman doing ski touring up a huge hill, naturally good looking without makeup or body altering surgery or injection, petite face, and looking intense and fun, square aspect ratio, awesome heavenly view, view from far"  # Replace with your desired term
    num_images = 1000  # Number of images to generate
    output_folder = "results/ski_touring"  # Folder to save the images

    main(term, num_images, output_folder)
