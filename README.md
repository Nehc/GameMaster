# GameMaster
Roleplay telegram game engine with ChatGPT backbone

### Several assumptions...

1. You got telegram bot-token and You have Open AI acc. It must be specified in [**docker-compose.yml**](https://github.com/Nehc/GameMaster/blob/main/docker-compose.yml)

3. You up local StableDffusion [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui) and set it entry-point URL in [**g_master/SD_api.py**](https://github.com/Nehc/GameMaster/blob/main/g_master/SD_api.py)

4. You has PROXY in local (or external) and set it URL in PROXY variable in [**g_master/main.py**](https://github.com/Nehc/GameMaster/blob/main/g_master/main.py)

if not... if not, fix it yourself! :)
