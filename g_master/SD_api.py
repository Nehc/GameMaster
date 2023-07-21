import os, requests, base64

sd_url = os.getenv('TG_TOKEN')

def gen_image(prompt,extra={}):
    '''
    https://github.com/AUTOMATIC1111/stable-diffusion-webui
    must be on http://devbox:7860, or change URL in sd_url
    '''
    payload = { "prompt": prompt, "steps": 20 }
    payload.update(extra)
    response = requests.post(url=f'{sd_url}/sdapi/v1/txt2img', json=payload)
    if response.status_code != 200:
        print( "Non-200 response: " + str(response.text))
        #bot.send_message(chat_id, "Non-200 response: " + str(response.text))
        return
    r = response.json()
    print(r['info'])
    images = [base64.b64decode(i.split(",",1)[0]) for i in r['images']]
    return images[0]
