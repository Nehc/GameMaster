# GameMaster
Roleplay telegram game engine with ChatGPT backbone

### Several assumptions...

1. You got your GameMaster telegram bot-token from BotFather and You have Open AI acc. These two parameters must be specified in [**docker-compose.yml**](https://github.com/Nehc/GameMaster/blob/main/docker-compose.yml)

3. You up local StableDffusion (https://github.com/AUTOMATIC1111/stable-diffusion-webui) and set it entry-point URL in [**g_master/SD_api.py**](https://github.com/Nehc/GameMaster/blob/main/g_master/SD_api.py)

4. You has PROXY in local and set it URL in PROXY variable in [**g_master/main.py**](https://github.com/Nehc/GameMaster/blob/main/g_master/SD_api.py)

if not... if not, fix it yourself! :)
