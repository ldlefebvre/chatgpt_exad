import openai
import os
import httpx
import uuid
import time
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

# Set up your OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')

client = openai.OpenAI(api_key=api_key)

# Function to generate an image based on a given term
def generate_image(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except openai.APIError as e:
        print(f"Failed to generate image: {e}")
        return None

# Function to save an image from a URL
async def save_image(image_url, save_path):
    if image_url:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
            else:
                print(f"Failed to retrieve image from {image_url}")
    else:
        print("No image URL provided")

# Main function to generate and save images
async def main(terms, num_images_per_term, output_folders):
    images_per_minute = 5
    request_timestamps = [0] * images_per_minute  # Initialize timestamps for rate limiting

    for term, output_folder in zip(terms, output_folders):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for i in range(num_images_per_term):
            # Find the next available slot
            next_available_slot = min(request_timestamps)
            current_time = time.time()
            sleep_time = max(60 - (current_time - next_available_slot), 0)

            if sleep_time > 0:
                print(f"Waiting for {sleep_time:.2f} seconds to respect rate limit...")
                await asyncio.sleep(sleep_time)

            print(f"Generating image {i+1}/{num_images_per_term} for term: {term}")
            image_url = generate_image(term)
            unique_id = uuid.uuid4()
            save_path = os.path.join(output_folder, f"{unique_id}.png")
            await save_image(image_url, save_path)
            print(f"Saved image {i+1}/{num_images_per_term} to {save_path}")

            # Update the timestamp for the current slot
            request_timestamps[request_timestamps.index(next_available_slot)] = time.time()

if __name__ == "__main__":
    terms = [
        "extreme sport athlete woman doing summer mountaineering, naturally good looking and looking intense and fun, chain of mountain in the distance",
        "extreme sport athlete woman snowmobiling, naturally good looking and looking intense and fun, chain of mountain in the distance",
    ]

    output_folders = [
        "results/mountaineering",
        "results/snowmobiling",
    ]

    num_images_per_term = 100

    asyncio.run(main(terms, num_images_per_term, output_folders))
