import openai, time

class ChatGPT:
    def __init__(self, api_key, proxy):
        self.api_key = api_key 
        self.proxy = proxy

    def recursive_API_call(self, prompt):
        try:
            openai.api_key = self.api_key 
            openai.proxy = self.proxy
            ans = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages= prompt
            )
        except Exception as e:
            print(e); time.sleep(20)
            ans = self.recursive_API_call(prompt)
        return ans

    def answer(self, prompt):
        ans = self.recursive_API_call(prompt)
        return ans.choices[0].message.content    