import discord
from discord.ext import commands, tasks
from discord import app_commands
import httpx, asyncio, os
import socket
import timeit
from dotenv import load_dotenv
import datetime, requests

load_dotenv()

llmapikey = int(os.environ.get('API_KEY'))
llmapihost = str(os.environ.get('API_URL'))
token = str(os.environ.get('DISCORD_TOKEN'))

class colors:
    default = 0
    teal = 0x1abc9c
    dark_teal = 0x11806a
    green = 0x2ecc71
    dark_green = 0x1f8b4c
    blue = 0x3498db
    dark_blue = 0x206694
    purple = 0x9b59b6
    dark_purple = 0x71368a
    magenta = 0xe91e63
    dark_magenta = 0xad1457
    gold = 0xf1c40f
    dark_gold = 0xc27c0e
    orange = 0xe67e22
    dark_orange = 0xa84300
    red = 0xe74c3c
    dark_red = 0x992d22
    lighter_grey = 0x95a5a6
    dark_grey = 0x607d8b
    light_grey = 0x979c9f
    darker_grey = 0x546e7a
    blurple = 0x7289da
    greyple = 0x99aab5

def send_request(data):
    response = requests.request("POST", llmapihost, headers={"Content-Type": "application/json", "Authorization": llmapikey}, json=data)
    if response.status_code == 200:
        try:
            response_data = response.json()
            # Extract the required information
            content = response_data['choices'][0]['message']['content']
            completion_tokens = response_data['usage']['completion_tokens']
            total_tokens = response_data['usage']['total_tokens']
            # Print the extracted information
            print(f"Content: {content}")
            return content, completion_tokens, total_tokens
        except ValueError as e:
            return "Error: " + str(e)
    else:
        return "Error: " + str(response.status_code)

    
def measure_latency(ip_address, port):
    def connect_socket():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip_address, port))
        sock.close()

    # Measure the time taken to establish a connection
    latency = timeit.timeit(connect_socket, number=1)
    latency_ms = latency * 1000
    return latency_ms

chatintents = discord.Intents.all()
global client
client = commands.Bot(command_prefix="oink ", help_command=None, intents=chatintents, owner_id=859368295823835136)

@tasks.loop(seconds=5)
async def changeStatus():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="with VerusCoins!"))
    await asyncio.sleep(3)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="for /ask command!"))
    await asyncio.sleep(3)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.competing, name="Verus Community!"))
    await asyncio.sleep(3)
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="𝙊𝙞𝙣𝙠 papa!"))
    await asyncio.sleep(3)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    changeStatus.start()
    try:
        synced = await client.tree.sync()
        print(f"Successfully Synced {len(synced)} commands..")
    except Exception:
        print("Failed to sync commands")
    print("Enabled status updates..")

# @client.tree.error
# async def on_app_command_error(interaction: discord.Interaction, error):
#     embeddoerr = discord.Embed(title="Woahh!!", description="**Slow down** I can't keep pinging my APIs. Try again in {:.2f}s".format(error.retry_after), color=colors.red)
#     embeddoerr.set_footer(text=f"Command Error invoked by {interaction.user.name} on {datetime.datetime.now()}")
#     return await interaction.response.send_message(embed=embeddoerr, ephemeral=True)

@client.tree.command(name="ask", description="Ask a question related to anything in the Verus Community!")
@app_commands.guild_only()
async def askquestion(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    try:
        data = {
        "model": "lmstudio-community/VerusCommunity",
        "messages": [
            {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
            {"role": "user", "content": question}
        ],
        "temperature": 0.05,
        "stream": False
        }
        answer, completion_tokens, total_tokens = await send_request(data)
        embed = discord.Embed(title=question, description=answer, color=colors.green)
        embed.set_footer(text=f"Invoked by {interaction.user.name} | {completion_tokens} tokens out of {total_tokens} total tokens generated.")
    except Exception as err:
        embed = discord.Embed(title="Boooo!!! Error", description=f"Sorry, I'm having trouble understanding that. ```{err}```", color=colors.red)
    await interaction.followup.send(embed=embed)
    
@client.tree.command(name="ping", description="Returns latency of the API and the bot!")
async def ping(interaction: discord.Interaction):
    await interaction.response.defer()
    response = f"Bot Latency: {round(client.latency * 1000)}ms"
    await interaction.followup.send(response, ephemeral=True)

client.run(token=token)