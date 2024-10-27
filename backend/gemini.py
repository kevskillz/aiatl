import os, time

import requests
import imageio
import io

from sat import ImgSat
import google.generativeai as genai


def upload_sat_img(link):

    response = requests.get(link)
    response.raise_for_status()

    gif_bytes = io.BytesIO(response.content)
    gif = imageio.mimread(gif_bytes, format='gif')


    video_bytes = io.BytesIO()
    imageio.mimsave(video_bytes, gif, format='mp4', fps=2)
    video_bytes.seek(0)
    
    response = genai.upload_file(video_bytes, mime_type='video/mp4')

    return response


def get_gemini_response(model, isat, lat, long, rag, state, county, zip, cost, per):

    link = isat.query(lat, long)
    video_file = upload_sat_img(link)
    
    while video_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(video_file.state.name)

    # Create the prompt.
    # prompt = "Hurricane damage has been getting much worse in recent years, and it is harder to live with it. Use the given video of satellite imagery and analyze it. Mention attached video showing sattelite imagery at least once."
    print(lat, long, state, zip, county)
    prompt = f"Analyze what you see in this video. This is satellite imagery at the latitude {lat} and longitude {long}. Mention location details in the state {state}, {county} county, and zip code {zip}. Mention what you see in this video with respect to the coordinates of the location and just talk about how hurricane prone the area is and perhaps average insurance costs in the future + advice to future home buyers in area. Also use documents to back claims. Talk about how the current average cost at this zipcode is ${cost}, which is {per}% above/below the national average. Do not say anything about wanting more data and do not provide links, and style the response so we can embed it as html (bold key terms and such). Make response BRIEF as possible."

    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

    # Debugging output
    print("Prompt:", prompt)
    print("Video File:", video_file)  # Adjust based on actual attributes
    print("RAG:", rag)

    # Make the LLM request.
    print("Making LLM inference request...")
    response = model.generate_content([video_file, rag, prompt],  # Ensure correct attribute
                                       request_options={"timeout": 600})
   
    print(response)
    genai.delete_file(video_file.name)
    return link, response.candidates[0].content.parts[0].text
