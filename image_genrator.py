import google.generativeai as genai
import dotenv
    # Configure your API key (replace 'YOUR_API_KEY' with your actual key)
genai.configure(api_key="YOUR_API_KEY")

    # Load the Gemini 3 Pro Image model
model = genai.GenerativeModel('gemini-3-pro-image-preview')


response = model.generate_content("A high-resolution photo of a futuristic city at sunset, with flying cars and towering skyscrapers.")

    # Access the generated image(s)
for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.inline_data:
                # This part contains image data, which can be saved or displayed
            image_data = part.inline_data.data
                # Example: Save the image to a file
            with open("generated_image.png", "wb") as f:
                f.write(image_data)
            print("Image generated and saved as generated_image.png")