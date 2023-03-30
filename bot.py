import discord
import dotenv
import logging
import os
import openai
from logging.handlers import RotatingFileHandler
from utilities import color, classroom, logger
from . import index

dotenv.load_dotenv()

openai.api_key = os.getenv('OPEN_API_KEY')
#print(openai.api_key)

def classify_intent(prompt):
    model_engine = "text-davinci-002"  # or any other OpenAI model that suits your use case

    # define the prompt to use for classification
    prompt = (f"Please classify the following user input into one of the following categories: "
              f"1. cheap\n2. expensive\n\n"
              f"User Input: {prompt}\nCategory:")

    logging.info("Prompt: ")
    logging.info(prompt)

    # send prompt to OpenAI's API for classification
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1,
        n=1,
        stop=None,
        temperature=0.5,
    )

    logging.info("Answer: ")
    logging.info(response)

    # retrieve the predicted intent code from the response
    predicted_intent = response.choices[0].text.strip().lower()

    # return the predicted intent code
    return predicted_intent

# create logger
def init_logging(logger):
    # logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    handler_rot_file = RotatingFileHandler(filename='discord-bot.log', encoding='utf-8', mode='a')
    handler_rot_file.setLevel(logging.DEBUG)
    handler_rot_file.setFormatter(log_formatter)

    handler_console = logging.StreamHandler()
    handler_console.setLevel(logging.DEBUG)
    handler_console.setFormatter(log_formatter)

    logger.addHandler(handler_rot_file)
    logger.addHandler(handler_console)

    return logger


logger = init_logging(logging.root)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        
        logging.info(f'Message from {message.author.name}: {message.content}')

        if message.content == 'ping':
            await message.channel.send('pong')
        
        if message.content == 'Hello!':
            await message.channel.send('Hi!')
            
        result = classify_intent(message.content)
        await message.channel.send(result)

bot_token = os.getenv('DISCORD_BOT_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
client.run(bot_token)
