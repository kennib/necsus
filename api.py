from flask import request, jsonify, send_from_directory
from crossdomain import crossdomain
import yaml

from flask_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint

from necsus import app, get_db
import events

SWAGGER_URL = '/docs'
API_URL = '/api/spec'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': 'NeCSuS'},
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/api/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = '1.0'
    swag['info']['title'] = 'NeCSuS API'
    return jsonify(swag)

BOT_SWAGGER_URL = '/bot/docs'
BOT_API_URL = '/bot/spec'
bot_swaggerui_blueprint = get_swaggerui_blueprint(
    BOT_SWAGGER_URL,
    BOT_API_URL,
    config={'app_name': 'Bot'},
    blueprint_name='bot_swagger_ui',
)
app.register_blueprint(bot_swaggerui_blueprint, url_prefix=BOT_SWAGGER_URL)

@app.route("/bot/spec")
def bot_spec():
    with app.open_resource('bot-spec.yml', mode='r') as f:
      swag = yaml.load(f)
    return jsonify(swag)

@app.route('/api/messages', methods=['GET'])
@crossdomain(origin='*')
def get_new_messages():
  """
        List messages
        ---
        tags:
          - messages
        parameters:
          - in: query
            name: room
            schema:
              type: string
            description: the name of the room
          - in: query
            name: since
            schema:
              type: integer
            description: the ID of the last message you already have
        responses:
          200:
            description: Messages since last message
            schema:
              id: Message
              properties:
                id:
                 type: integer
                 example: 1
                 description: the messages's unique ID
                room:
                 type: string
                 example: tutors
                 description: the room the message was posted in
                author:
                 type: string
                 example: Georgina
                 description: the author of the message
                text:
                 type: string
                 example: Hello, World!
                 description: the message's text
  """
  since_id = request.values.get('since')
  room = request.values.get('room')

  db = get_db()
  new_messages = list(db.messages.new(since_id, room=room))

  return jsonify(new_messages)

@app.route('/api/bots', methods=['GET'])
@crossdomain(origin='*')
def get_bots():
  """
        List Bots
        ---
        tags:
          - bots
        parameters:
          - in: query
            name: room
            schema:
              type: string
            description: the name of the room to list bots for
        responses:
          200:
            description: Bots and their endpoints
            schema:
              type: array
              items:
                id: Bot
                properties:
                  id:
                   type: integer
                   example: 1
                   description: the bot's unique ID
                  name:
                   type: string
                   example: NeCSuS Bot
                   description: the bot's name
                  url:
                   type: string
                   example: https://necsus-bot.ncss.cloud
                   description: the bot's url
  """
  room = request.values.get('room')

  db = get_db()

  if room != None:
    bots = list(db.bots.find_all(room=room))
    return jsonify(bots)
  else:
    bot = db.bots.list()
    return jsonify(bot)

@app.route('/api/actions/bot', methods=['POST'])
@crossdomain(origin='*')
def post_bot():
  """
        Create or Update a Bot
        ---
        tags:
          - bots
        parameters:
          - in: query
            name: id
            schema:
              type: integer
            description: the ID of the bot to update, creates a new bot if no is ID given
          - in: query
            name: room
            schema:
              type: string
            description: the name of the room the bot is in, the bot's room is not updated if no room parameter is given
          - in: query
            name: name
            schema:
              type: string
            description: the name of the bot, the bot's name is not updated if no url parameter is given
          - in: query
            name: responds_to
            schema:
              type: string
            description: a regular expression for matching messages to send to the bot, not updated if the parameter is not given
          - in: query
            name: url
            schema:
              type: string
            description: the URL endpoint for the bot, the bot's url is not updated if no url parameter is given
        responses:
          200:
            description: Returns a bot
            schema:
              id: Bot
              properties:
                id:
                 type: integer
                 example: 1
                 description: the bot's unique ID
                name:
                 type: string
                 example: Repeat Bot
                 description: the bot's name
                responds_to:
                 type: string
                 example: repeat (?P<word>\w+) (?P<count>\d+) times
                 description: the regular expression that the bot listens for in messages
                url:
                 type: string
                 example: https://repeat-bot.kennib.repl.co
                 description: the bot's url
  """
  room = request.values.get('room')
  id = request.values.get('id')
  name = request.values.get('name')
  responds_to = request.values.get('responds_to')
  url = request.values.get('url')

  db = get_db()
  bot = db.bots.update_or_add(id=id, room=room, name=name, responds_to=responds_to, url=url)

  return jsonify(bot)

@app.route('/api/actions/bot', methods=['DELETE'])
@crossdomain(origin='*')
def delete_bot():
  """
        Remove a Bot
        ---
        tags:
          - bots
        parameters:
          - in: query
            name: id
            schema:
              type: integer
            description: the ID of the bot to update, creates a new bot if no is ID given
        responses:
          200:
            description: Returns the ID of the removed bot
            schema:
              properties:
                id:
                 type: integer
                 example: 1
                 description: the bot's unique ID
  """
  id = request.values.get('id')

  db = get_db()
  bot = db.bots.remove(id)

  return jsonify({id: id})

@app.route('/api/actions/message', methods=['POST'])
@crossdomain(origin='*')
def post_message():
  """
        Post a message to a room
        ---
        tags:
          - messages
        parameters:
          - in: body
            description: thing
            name: content
            required: true
            schema:
              type: object
              required:
                - room
                - author
                - text
              properties:
                room:
                  type: string
                  example: 'party-room'
                author:
                  type: string
                  nullable: true
                  example: 'Kenni'
                text:
                  type: string
                  example: 'Hello sam'

        responses:
          200:
            description: The message was successfully posted.
            schema:
              id: Message
  """

  data = request.get_json()
  # room is allowed to be blank because "" is a room
  if not data or not data.get('text') or data.get('room') is None or not data.get('author'):
    return jsonify({'message': 'text, room, and author keys are required'}), 400

  db = get_db()

  message = {
    'text': str(data['text']),
    'room': str(data['room']),
    'author': str(data['author']),
  }
  message_result = events.trigger_message_post(db, message)

  return jsonify(message_result)

@app.route('/api/actions/reset-room', methods=['POST'])
@crossdomain(origin='*')
def reset_room():
  """
        Remove a room's messages
        ---
        tags:
          - room
        parameters:
          - in: query
            name: room
            schema:
              type: string
        responses:
          200:
            description: Room
            schema:
              id: Message
              properties:
                room:
                 type: string
                 example: tutors
                 description: the room that was reset
  """

  room = request.values['room']

  db = get_db()
  events.trigger_room_reset(db, room)

  return jsonify({'room': room})
