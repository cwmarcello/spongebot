# Takes messages from anyone in the "Mocked" role and responds with the same text in
# a mocking spongebob-style.

import os
import random
import logging

import discord
from dotenv import load_dotenv

load_dotenv() # loads in environment variables from .env (for secrets)
client = discord.Client()

# Logging config
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='spongebot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # don't send responses to yourself if you made the bot have the mocked role
    if message.author == client.user:
        return

    # Respond to mentions of the spongebot role
    for role in message.role_mentions:
        if "spongebot" in role.name.lower():
            logger.info(f"Role {role.name.lower()} mentioned, responding")
            response = create_response_to_mention(message)
            await message.channel.send(response, reference=message)
            return

    # Respond to mentions of the spongebot user
    for user in message.mentions:
        if "spongebot" in user.name.lower():
            logger.info(f"User {user.name.lower()} mentioned, responding")
            response = create_response_to_mention(message)
            await message.channel.send(response, reference=message)
            return

    # Check if a user has the "mocked" role and if so respond
    if "mocked" in [role.name.lower() for role in message.author.roles]:
        if message.content != '':
            # blacklist link strings and animated emojis to prevent bad mocks
            blacklist_strings = ["www.", ".html", ".gif", ".com", ".org", ".net", "<a:"]
            if not any(x in message.content for x in blacklist_strings):
                logger.info(0.01*len(message.content))
                if random.random() < (0.01 * len(message.content)):
                    logger.info("Detected mockable message from user: " + message.author.name)
                    mocked_message = mock_string(message.content)

                    await message.channel.send(mocked_message)
                    logger.info("Message Mocked ('" + mocked_message + "')")

@client.event
async def on_message_edit(before, after):
    # safety stop, like above
    if after.author == client.user or before.author == client.user:
        return

    # checks if the person editing the message is to be mocked
    if "mocked" in [role.name.lower() for role in after.author.roles]:
        if before.content != '':
            logger.info("Detected edit of mocked message from user: " + after.author.name + ", remocking")
            remocked_message = mock_string(after.content) # create the mock of the edit
            
            # Get the messages after the edited message (so we can find our spongebot response)
            # see docs here https://discordpy.readthedocs.io/en/latest/api.html#discord.TextChannel.history
            async for response in before.channel.history(limit=5, after=before):
                if response.author == client.user:
                    spongebot_response = response
                    break
            else:
                logger.warning("Spongebot response not found.")
                return 
                
            logger.debug(spongebot_response.content)
            await spongebot_response.edit(content=remocked_message)
            logger.info("Edited Message re-mocked ('" + remocked_message + "')")

@client.event
async def on_message_delete(message):
    # safety stop, like above:
    if message.author == client.user:
        return
    
    if "mocked" in [role.name.lower() for role in message.author.roles]:
        if message.content != '':      
            logger.info("Detected deletion of mocked message from user: " + message.author.name)

            # Get the messages after the edited message (so we can find our spongebot response)
            # see docs here https://discordpy.readthedocs.io/en/latest/api.html#discord.TextChannel.history
            async for response in message.channel.history(limit=5, after=message):
                if response.author == client.user:
                    spongebot_response = response
                    break
            else:
                logger.warning("Spongebot response not found. Maybe they deleted a message with no content?")
                return 

            edit_messages = [f"You think you're so clever, deleting your message.",
                            f"Did you really think deleting your message would save you?",
                            f"Yeah you better take that back.",
                            mock_string(f"My name is {message.author.name} and I delete my messages."),
                            f"You can run, you can hide. Spongebot always follows.",
                            f"Hey {message.author.name}! I think you dropped this:"]

            chosen_message = random.choice(edit_messages)

            chosen_message += f"\nDeleted Message by {message.author.name}: *{message.content}*"

            await spongebot_response.edit(content=chosen_message)
            logger.info("Mocking Message changed to ('" + chosen_message + "')")

# Lets admins (and myself) remove mocking messages by giving them a thumbs down emoji
# useful for bugged reactions or just annoying spam
@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == client.user:
        if (user.name.lower() == os.getenv('USERNAME')) or ("admin" in [role.name.lower() for role in user.roles]):
            if reaction.emoji == "\U0001F44E":
                logger.info(f"Mod {user.name} deleted the following mocking message:\n'{reaction.message.content}'")
                await reaction.message.delete()

# Takes in a string and mocks it
def mock_string(str_to_mock: str):

    logger.debug(str_to_mock)
    
    str_to_mock = str_to_mock.lower().strip("*")
    str_to_mock = str_to_mock.replace("*", "")
    str_to_mock = "***" + str_to_mock + "***"
    logger.debug("Formatted String (Pre-Mock): " + str_to_mock)

    mocked_str_array = []
    lastUpper = False
    for char in str_to_mock.lower():
        if lastUpper == False:
            mocked_str_array.append(char.upper())
            if random.random() < 0.9:
                lastUpper = True
            
        else:
            mocked_str_array.append(char)
            if random.random() < 0.9:
                lastUpper = False

    mocked_str = ""
    mocked_str = mocked_str.join(mocked_str_array)
    logger.debug(mocked_str)
    return mocked_str

# Responds to a mention of the bot
def create_response_to_mention(message):
    if "mocked" in [role.name.lower() for role in message.author.roles]:
        responses = [
            "The fuck did you just say about me you tartar sauce chugging barnacle hugger?",
            "I'll carve you into pieces and serve you as krabby patty meat",
            "Get back to flirting with a computer like the plankton wannabee you are",
            "The Spongebot finds your attempts at communication pitiful",
            "cry some more",
            "you're as ugly as the hash-slinging slasher with none of the charm"
        ]
        response = ("***" + random.choice(responses) + "***")
    else:
        '''
        responses = [
            "I'm ready, I'm ready!", "Order up!", "Aye-aye, Captain!", "No problemo.", "***hello there***",
            "You called?", "Sup?", "'sah dude", "\U0001F609", "\U0001F618",
            "<:StAlLoNeBoB:615204461459275818>", "<:CaVeBoB:615205197056049162>"
        ]
        '''
        responses = [
            "\U0001F609", "\U0001F618", "<:StAlLoNeBoB:615204461459275818>",
            "<:CaVeBoB:615205197056049162>", "<:SmUgBOb:615202190100791306>", "<:SmiRK:856927495185367073>"
        ]
        responses.extend(message.guild.emojis)
        response = random.choice(responses)
    return response


client.run(os.getenv('TOKEN'))