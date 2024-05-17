from openai import OpenAI
import base64
import requests
import json
client = OpenAI()

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

class Agent:
    def __init__(self,system_prompt=None):
        """Initializes the object"""
        # Initialize instance variables here
        self.messages=[]
        self.response=None
        if system_prompt is not None:
            self.messages.append(
                {
      "role": "system",
      "content": [
        {"type": "text", "text": system_prompt},
      ],
    }
            )

    def chat(self,prompt,images,print_flag=True):
        """Method 1 description"""
        content=[] # Method 1 implementation
        content.append(
        {"type": "text", "text": prompt})
        for image in images:
            content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}",
            }})
        self.messages.append(
            {"role": "user",
            "content": content})
        
        response = client.chat.completions.create(
        model="gpt-4o",
        messages=self.messages,
        max_tokens=300,
        )
        self.response=response

        choices = json.loads(self.response.json())['choices']
        if print_flag==True:
            for choice in choices:
                print(choice['message']['content'])
                