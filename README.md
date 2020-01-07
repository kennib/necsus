# NeCSuS

[NeCSuS](https://chat.ncss.cloud) is a chat app which makes it simple to connect "bots" (i.e., simple HTTP servers that reply to messages).
NeCSuS has the ability to host chats in "rooms", listen to voice commands and speak chat messages out loud.


## API

Documentation on the API can be found on [the main NeCSuS server](https://chat.ncss.cloud/docs) or at `/docs` on your local instance.


## FAQ

### What is NeCSuS?
An web app that allows you to create rooms in which you can import and interact with chatbots.

### How do I post (images|links|formatted text)?
The client uses [markdown-it](https://markdown-it.github.io) to render the text.
This means you need to use plain text to post any content.
Look at the [demo page](https://markdown-it.github.io) to see examples of the plain text used to post (images|links|formatted text).

### How do I create a room?
The simplest way to create a room is to add your name onto the end of your group's room such that it has the form:
https://chat.ncss.cloud/group<group_number>-<your_name>

For example: https://chat.ncss.cloud/group4-kenni

### How do I create a bot? 
All bots should consist of 3 main elements:
  * route
  * [input](#how-do-i-send-input-from-necsus-to-my-bot)
  * [output](#what-output-should-i-send-from-my-bot-back-to-necsus)

### How do I link my bot to a room? 

Clicking on the **"open settings"** button at the top right hand section of the page, we can see a new side panel open up.
Under the red **reset room** button - press the "add bot" button to create a new blank bot. 
From there, fill in the bot name (preferably something unique and not normally used in a sentence).
You can then post the base link for the bot.

### How do I send input from NeCSuS to my bot?

Every time a message is sent by a user to a room - NeCSuS scans the message to see if there is a message that matches either an existing `bot name`, or the `Responds to` field for all active bots in the chatroom. 
Depending on the contents of the `Responds to` field - the data will be sent to the bot either as plain text or it will have additional `key:value` pairs

#### I want key value pairs!!
Awesome! You can use named capturing groups to do this. For example, [repeat bot](https://repl.it/@kennib/repeat-bot) requires two things from a message:
  * A string to repeat (lets call this `word`)
  * How many times to repeat it (lets call this `count`)

We can then use the following regex string in the `Responds to` field of our NeCSuS bot to get these: 

`repeat (?P<word>\w+) (?P<count>\d+) times`

So, if I sent the message `repeat hello 5 times` to a chatroom with repeat bot - NeCSuS would send data in the following way.
```JSON
{
    "room": "shrey", 
    "author": "Anonymous", 
    "text": "repeat hello 5 times", 
    "params": {
                "word": "hello", 
                "count": "5"
              }
}
```

>you can get this data by using request.get_json() in your python server :) 

### What output should I send from my bot back to NeCSuS

NeCSuS expects two things to be returned as JSON from bot. 
So, a basic server that sends the same message every time should look like:

```py3
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/', methods=['POST'])
def home_handler():
  # Create a message to send to NeCSuS
  message = {
    'author': 'Appreciation Bot',
    'text': "Yay! I'm here to tell you that you did a great job!",
  }

  # Return the JSON
  return jsonify(message)

app.run(host='0.0.0.0')
```

So, every time this bot is activated - it will send the same message back: `Yay! I'm here to tell you that you did a great job!"`
