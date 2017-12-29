from discord import *
import asyncio
import ast
import time
import random
client = Client()
properties = open("RPG.properties")
values = properties.readlines()
properties.close()
prototypeItem = {
    "name": "PROTOTYPE ITEM",
    "takeable": False,
    "interactable": True,
    "interactAction": [["touch the {0}","{1} touched the {0}"],["use the {0}","{1} used the {0}"]],
    "throwable": False,
    "throwFail": "The {0} is too heavy to be thrown",
    "throwSucceed": "{1} threw the {0}",
    "throwPlayer": "{1} threw the {0} at {2}! Luckily it didn't hit...",
    "breakChance": 0.0,
    "breakMsg": "The {0} broke!"
}
prototypeRoom = {
    "name": "PROTOTYPE ROOM",
    "items": [],
    "notes": {}
}
prototypePlayer = {
    "name": "PROTOTYPE PLAYER",
    "money": 0,
    "inventory": []
}
owner2 = "[your id here]"
playerSave = open("players.sav","r")
players = ast.literal_eval(playerSave.read())
playerSave.close()
itemSave = open("items.sav","r")
items = ast.literal_eval(itemSave.read())
itemSave.close()
roomSave = open("rooms.sav","r")
rooms = ast.literal_eval(roomSave.read())
roomSave.close()
token = values[0].strip("\n")
prefix = values[1].strip("\n")
owner = values[2].strip("\n")
curItem = None
def parse(input):
    global prefix
    if input.startswith(prefix):
        return input[1:].split(" ")
    else:
        return False
@client.event
async def on_ready():
    global owner
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print("Owner: {0}".format(owner))
    print('------')
@client.event
async def on_message(message):
    global curItem, owner, prototype, prefix, rooms, items
    command = parse(message.content)
    if not command:
        return
    if curItem != None:
        if message.author.id != owner and str(message.author.id) != owner2:
            return
        if command[0] == "show":
            await client.send_message(message.channel, repr(curItem))
        elif command[0] == "set":
            if len(command) >= 3:
                attribute = command[1]
                if curItem.get(attribute, -1) == -1:
                    await client.send_message(message.channel, "{0} is not a valid attribute for an item!".format(attribute))
                else:
                    if type(curItem[attribute]) is str:
                        curItem[attribute] = " ".join(command[2:])
                    elif type(curItem[attribute]) is float:
                        try:
                            curItem[attribute] = float(command[2])
                        except:
                            await client.send_message(message.channel, "Argument of type float required for attribute {0}, type {1} supplied! ({2})".format(attribute,type(command[2]),command[2]))
                    elif type(curItem[attribute]) is bool:
                        test = ast.literal_eval(command[2])
                        if type(test) is bool:
                            curItem[attribute] = test
                        else:
                            await client.send_message(message.channel, "Argument of type bool required for attribute {0}, type {1} supplied! ({2})".format(attribute,type(command[2]),command[2]))
            else:
                await client.send_message(message.channel, "Not enough arguments supplied to set! ({0} < 3)".format(len(command)))
        elif command[0] == "confirm":
            if len(command) > 1:
                id = command[1]
                items[id] = curItem
                curItem = None
                await client.send_message(message.channel, "Item added! This item has item ID {0}. You can place this in a room with `{1}summon {0}`, but only do this once! If you need another one, repeat this process with a different ID.".format(id, prefix))
            else:
                await client.send_message(message.channel, "You need to specify an ID. Used IDs: {0}".format(", ".join(items.keys())))
        elif command[0] == "cancel":
            curItem = None
            await client.send_message(message.channel, "Cancelled!")
    else:
        if command[0] == "newItem" and (message.author.id == owner or str(message.author.id) == owner2):
            curItem = prototypeItem
            await client.send_message(message.channel, "Creating new item")
        elif command[0] == "stop" and str(message.author.id) == owner2:
            await client.send_message(message.channel, "Stopping...")
            await client.logout()
        else:
            try:
                if command[0] == "summon" and (message.author.id == owner or str(message.author.id) == owner2):
                    if command[1] in items.keys():
                        if rooms.get(message.channel.id, -1) == -1:
                            await client.send_message(message.channel, "This room is not initialised! Initialise it with `{0}addroom [name]`!".format(prefix))
                        else:
                            rooms[message.channel.id]["items"].append(command[1])
                            await client.send_message(message.channel, "Added item {0} to room {1}".format(command[1],rooms[message.channel.id]["name"]))
                    else:
                        await client.send_message(message.channel, "The item {0} doesn't exist!".format(command[1]))
                elif command[0] == "addroom" and (message.author.id == owner or str(message.author.id) == owner2):
                    if len(command) < 2:
                        await client.send_message(message.channel, "You need to specify a name!")
                    else:
                        tmp = prototypeRoom
                        tmp["name"] = " ".join(command[1:])
                        rooms[message.channel.id] = tmp
                        await client.send_message(message.channel, "This channel is now an empty room, going by the name of {0}.".format(tmp["name"]))
                elif command[0] == "roomitems":
                    if rooms.get(message.channel.id, -1) == -1:
                        await client.send_message(message.channel, "This room is not initialised (and therefore contains no items)! Initialise it with `{0}addroom [name]`!".format(prefix))
                    else:
                        itmps = rooms[message.channel.id]["items"]
                        itmp5 = []
                        for i in itmps:
                            itmp5.append(i + ": " + items[i]["name"])
                        await client.send_message(message.channel, "Items in {0}: {1}".format(rooms[message.channel.id]["name"],", ".join(itmp5)))
                elif command[0] == "join":
                    if len(command) < 2:
                        await client.send_message(message.channel, "You need to specify a name!")
                    else:
                        tmp = prototypePlayer
                        tmp["name"] = " ".join(command[1:])
                        players[message.author.id] = tmp
                        await client.send_message(message.channel, "Your player character now has an empty inventory. You go by the name of {0}.".format(tmp["name"]))
                elif command[0] == "take" or command[0] == "steal":
                    if players.get(message.author.id, -1) == -1:
                        await client.send_message(message.channel, "Your player character is not initialised, meaning you have no inventory (and may not perform this action)! Initialise yourself with `{0}join [name]`!".format(prefix))
                    else:
                        item = command[1]
                        try:
                            if items[item]["takeable"]:
                                room = rooms[message.channel.id]
                                try:
                                    index = room["items"].index(item)
                                    
                                    del room["items"][index]
                                    players[message.author.id]["items"].append(item)
                                    await client.send_message(message.channel, "You stole the {0}!".format(items[item]))
                                except:
                                    index = -1
                                    await client.send_message(message.channel, "You cannot steal that; it is not in this room!")
                            else:
                                await client.send_message(message.channel, "This item cannot be taken!")
                        except:
                            await client.send_message(message.channel, "You cannot steal that; it does not exist!")
                elif command[0] == "place" or command[0] == "return":
                    if players.get(message.author.id, -1) == -1:
                        await client.send_message(message.channel, "Your player character is not initialised, meaning you have no inventory (and may not perform this action)! Initialise yourself with `{0}join [name]`!".format(prefix))
                    else:
                        item = command[1]
                        player = players[message.author.id]
                        room = rooms[message.channel.id]
                        try:
                            index = player["items"].index(item)
                            del player["items"][index]
                            room["items"].append(item)
                            await client.send_message(message.channel, "You placed the {0} in the {1}!".format(items[item], room))
                        except:
                            index = -1
                            await client.send_message(message.channel, "You cannot place that; it does not exist (or you do not have it)!")
                elif command[0] == "inventoryitems":
                    if players.get(message.author.id, -1) == -1:
                        await client.send_message(message.channel, "Your player character is not initialised (and therefore has no inventory)! Initialise yourself with `{0}join [name]`!".format(prefix))
                    else:
                        itmps = rooms[message.channel.id]["items"]
                        itmp5 = []
                        for i in itmps:
                            itmp5.append(i + ": " + items[i]["name"])
                        await client.send_message(message.channel, "Items in {0}'s inventory: {1}".format(players[message.author.id]["name"],", ".join(itmp5)))
                elif command[0] == "save":
                    start = time.time()
                    playerSave = open("players.sav","w")
                    playerSave.write(repr(players))
                    playerSave.close()
                    itemSave = open("items.sav","w")
                    itemSave.write(repr(items))
                    itemSave.close()
                    roomSave = open("rooms.sav","w")
                    roomSave.write(repr(rooms))
                    roomSave.close()
                    end = time.time()
                    timeTaken = end - start
                    await client.send_message(message.channel, "Saved in {0}ms!".format(timeTaken * 1000))
                elif command[0] == "interact":
                    if players.get(message.author.id, -1) == -1:
                        await client.send_message(message.channel, "Your player character is not initialised and may not perform this action! Initialise yourself with `{0}join [name]`!".format(prefix))
                    else:
                        item = command[1]
                        try:
                            if items[item]["interactable"]:
                                options = items[item]["interactAction"]
                                try:
                                    option = int(command[2])
                                    await client.send_message(message.channel, options[option][1].format(items[item]["name"], players[message.author.id]["name"]))
                                except ValueError as e:
                                    print(e)
                                    await client.send_message(message.channel, "The interaction argument must be a number!")
                                except IndexError as e:
                                    print(e)
                                    out = "```You can:"
                                    for i in range(len(options)):
                                        out += "\n{0}: {1}".format(i,options[i][0].format(items[item]["name"]))
                                    out += "```"
                                    await client.send_message(message.channel, out)
                        except:
                            await client.send_message(message.channel, "That item does not exist!")
                elif command[0] == "throw":
                    if players.get(message.author.id, -1) == -1:
                        await client.send_message(message.channel, "Your player character is not initialised and may not perform this action! Initialise yourself with `{0}join [name]`!".format(prefix))
                    else:
                        item = command[1]
                        try:
                            if item in rooms[message.channel.id]["items"] or item in players[message.author.id]["items"]:
                                if items[item]["throwable"]:
                                    breakChance = items[item]["breakChance"]
                                    thrownAt = message.mentions
                                    if len(thrownAt) > 0:
                                        target = thrownAt[0].id
                                    else:
                                        target = None
                                    if target == None:
                                        out = items[item]["throwSucceed"].format(items[item]["name"],players[message.author.id]["name"])
                                    else:
                                        out = items[item]["throwPlayer"].format(items[item]["name"],players[message.author.id]["name"],players[target]["name"])
                                    print("Break?")
                                    if random.random() < breakChance:
                                        print("Break")
                                        out += "\n" + items[item]["breakMsg"].format(items[item]["name"])
                                        if item in rooms[message.channel.id]["items"]:
                                            rooms[message.channel.id]["items"].remove(item)
                                        else:
                                            players[message.author.id]["items"].remove(item)
                                        del items[item]
                                    else:
                                        print("No break")
                                else:
                                    out = items[item]["throwFail"].format(items[item]["name"])
                            else:
                                out = "You can't throw an item that isn't here!"
                            await client.send_message(message.channel, out)
                        except Exception as e:
                            print(e)
                            await client.send_message(message.channel, "That item does not exist!")
            except IndexError as e:
                await client.send_message(message.channel, "Not enough arguments supplied!")
                print(e)
"""/steal (item) /take (item) = Takes (item) to inventory [DONE]
/interact = Go to (item) and see the actions we can do with it [DONE]

[POSTPONE]
/sleep on (item) = Turn on sleep mode.
/wake (person) = Wakes up a sleeping user.
Possible commentary :
"{user} gently shakes (person)'s shoulder.
(person) slowly grunts."
"(person) opens their eyes. You seem to bother them."
[ENDPOSTPONE]

/throw (item) = Throws an item [DONE]
/throw (item) at (person) = Throws the (item) at (person). Can deal damage if an hp program is set [DONE, NO HP]

/shop = Sets up a list of items you can buy to decorate / do specific action with specific items
/buy (item) = Buys an item.
/sell (item) = Sells an item.

/note (item) [Write note here] = Leaves a note on a selected item, that the other users will see when they will use it."""
client.run(token)
