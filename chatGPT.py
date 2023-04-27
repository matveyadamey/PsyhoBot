import openai
import config

class ChatGPT:
    def ask(self,prompt):
        c=config.Config()
        key=c.put("openai_token")
        openai.api_key=key
        completion = openai.Completion.create(engine="text-davinci-003",
                                                  prompt=prompt,
                                                  temperature=0.5,
                                                  max_tokens=1000)
        return completion.choices[0]['text']
