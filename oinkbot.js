const { Client, GatewayIntentBits, ActivityType, EmbedBuilder, REST, Routes } = require('discord.js');
const axios = require('axios');
const dotenv = require('dotenv');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

dotenv.config();

const llmapikey = process.env.API_KEY;
const llmapihost = process.env.API_URL;
const token = process.env.DISCORD_TOKEN;

const colors = {
    default: 0,
    teal: 0x1abc9c,
    dark_teal: 0x11806a,
    green: 0x2ecc71,
    dark_green: 0x1f8b4c,
    blue: 0x3498db,
    dark_blue: 0x206694,
    purple: 0x9b59b6,
    dark_purple: 0x71368a,
    magenta: 0xe91e63,
    dark_magenta: 0xad1457,
    gold: 0xf1c40f,
    dark_gold: 0xc27c0e,
    orange: 0xe67e22,
    dark_orange: 0xa84300,
    red: 0xe74c3c,
    dark_red: 0x992d22,
    lighter_grey: 0x95a5a6,
    dark_grey: 0x607d8b,
    light_grey: 0x979c9f,
    darker_grey: 0x546e7a,
    blurple: 0x7289da,
    greyple: 0x99aab5
};

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent
    ]
});

const sendRequest = async (data) => {
    const response = await axios.post(llmapihost, data, {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': llmapikey
        },
        timeout: 100000
    });
        const responseData = response.data;
        const content = responseData.choices[0].message.content;
        const completionTokens = responseData.usage.completion_tokens;
        const totalTokens = responseData.usage.total_tokens;
        return { content, completionTokens, totalTokens };
};

const measureLatency = async (ipAddress, port) => {
    try {
        const start = Date.now();
        await execPromise(`nc -zv ${ipAddress} ${port}`);
        const latency = Date.now() - start;
        return latency;
    } catch (error) {
        console.error('Error measuring latency:', error);
        return null;
    }
};

client.once('ready', async () => {
    console.log(`We have logged in as ${client.user.tag}`);
    const rest = new REST({ version: '10' }).setToken(token);

    try {
        const commands = await rest.put(
            Routes.applicationCommands(client.user.id),
            { body: [
                {
                    name: 'ask',
                    description: 'Ask a question related to anything in the Verus Community!',
                    options: [
                        {
                            name: 'question',
                            type: 3, // STRING
                            description: 'The question you want to ask',
                            required: true
                        }
                    ]
                },
                {
                    name: 'ping',
                    description: 'Returns latency of the API and the bot!'
                }
            ] }
        );
        console.log(`Successfully registered ${commands.length} commands.`);
    } catch (error) {
        console.error('Error registering commands:', error);
    }

    changeStatus();
});

const changeStatus = async () => {
    const activities = [
        { name: 'with VerusCoins!', type: ActivityType.Playing },
        { name: 'for /ask command!', type: ActivityType.Watching },
        { name: 'Verus Community!', type: ActivityType.Competing },
        { name: '𝙊𝙞𝙣𝙠 papa!', type: ActivityType.Listening }
    ];
    let index = 0;
    setInterval(() => {
        client.user.setActivity(activities[index]);
        index = (index + 1) % activities.length;
    }, 5000);
};

client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;

    if (interaction.commandName === 'ask') {
        await interaction.deferReply();
        const question = interaction.options.getString('question');

        try {
            const data = {
                "model": "lmstudio-community/VerusCommunity",
                "messages": [
                    {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.05,
                "stream": false
            };
            const { content, completionTokens, totalTokens } = await sendRequest(data);

            const embed = new EmbedBuilder()
                .setTitle(question)
                .setDescription(content)
                .setColor(colors.green)
                .setFooter({ text: `Invoked by ${interaction.user.tag} | ${completionTokens} tokens out of ${totalTokens} total tokens generated.` });

            await interaction.editReply({ embeds: [embed] });
        } catch (error) {
            const embed = new EmbedBuilder()
                .setTitle('Boooo!!! Error')
                .setDescription(`Sorry, I'm having trouble understanding that. \`\`\`${error.message}\`\`\``)
                .setColor(colors.red);

            await interaction.editReply({ embeds: [embed] });
        }
    } else if (interaction.commandName === 'ping') {
        await interaction.deferReply();
        const latency = await measureLatency(llmapihost, llmapiport);
        const response = `Bot Latency: ${Math.round(client.ws.ping)}ms\nAPI Latency: ${latency ? `${latency}ms` : 'Error measuring latency'}`;
        await interaction.editReply(response);
    }
});

client.login(token);