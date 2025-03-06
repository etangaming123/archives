# [ modules ]
import ollama
import json
import pickle
import os

# [ data ]
if not os.path.exists("characters.json"):
    input("It seems that you don't have a characters JSON file.\nWould you like to create one in the same directory\nas this script? [Hit enter to confirm, or CTRL + C to quit]")
    print("Creating new file...")
    with open("characters.json", "wb") as file:
        json.dump({"sample character (always a lowercase name)": {"Description": "Describe your character here. This is visible to the user.", "Definition": "How should the ai play as this character? Describe the character's appearance, personality, and optionally add in how the ai greets the user!"}}, fp=file)
    print("Created new file!")

if not os.path.exists("savedchats.pkl"):
    input("It seems that you don't have a saved chats PKL file.\nWould you like to create one in the same directory\nas this script? [Hit enter to confirm, or CTRL + C to quit]")
    print("Creating new file...")
    with open("savedchats.pkl", "wb") as file:
        pickle.dump({}, file=file)
    print("Created new file!")

with open("characters.json", "rb") as file:
    characterinfo = json.load(file)

with open("savedchats.pkl", "rb") as file:
    savedchats = pickle.load(file)

currentchatname = ""
currentmodel = "gemma2:9b"

prompt = "You are the following character from now on. Your responses should match what the character would do after. Only generate responses for the character and not for anyone else. Here's their details: "

# [ functions // commands ]
def changeModel():
    global currentmodel
    print(f"Your current model: {currentmodel}")
    print("Avaliable models:")
    modellist = ollama.list()
    for item in modellist["models"]:
        print(f"{item['name']}")
    print("Select an ollama model (leave blank to cancel):")
    userinput = input(">> ")
    if not userinput == "":
        currentmodel = userinput
        print(f"Changed model to {currentmodel}!\n")

def saveData(newdata):
    with open("savedchats.pkl", "wb") as file:
        pickle.dump(newdata, file)

def saveChat(forcedifferentname):
    global currentchatname; global conversation_history; global savedchats
    if currentchatname == "" or forcedifferentname:
        print("Enter a name to save this chat as.")
        userinput = input(">> ")
        savedchats[userinput] = conversation_history
        currentchatname = userinput
        saveData(savedchats)
        print(f"Saved chat as {currentchatname}!\n")
    else:
        savedchats[currentchatname] = conversation_history
        saveData(savedchats)
        print(f"Saved chat as {currentchatname}!\n")

print("Powered by Ollama, coded by etangaming123.\n[the way this script saves data is incredibly scuffed sorry]\n\nPlease note that the first response will take a while to generate.")
while True:
    # [ select action ]
    print("\nEnter a valid command. ? for command list.\nYou can also run /? when chatting to a character to view commands there.")
    while True:
        userinput = input("> ").lower()
        if userinput == "?":
            print("Here are a list of valid commands:\nnew - Creates a new chat with a specified character\nchar - Lists all avaliable characters\nload - Loads a saved chat\nlist - Lists all your saved chats\ndelete - Deletes a saved chat\nmodel - Changes your Ollama model\nhelp - displays help information\nfilesizes - displays approximate file sizes for each chat\nexit - self explanatory")
        elif userinput == "new":
            print("Select a character to chat with.")
            userinput = input(">> ").lower()
            if userinput in characterinfo.keys():
                characterchoice = userinput
                break
            else:
                print("That character does not exist.")
        elif userinput == "char":
            print("Character list:")
            for charname, items in characterinfo.items():
                print(f"{charname} - {items['Description']}")
        elif userinput == "load":
            print("Select a saved chat name to load.")
            userinput = input(">> ")
            if userinput in savedchats.keys():
                currentchatname = userinput
                conversation_history = savedchats[currentchatname]
                break
            else:
                print("That saved chat does not exist.")
        elif userinput == "list":
            stringo = "Saved chats list: "
            for item in savedchats.keys():
                stringo = stringo + f"{item}, "
            print(stringo)
        elif userinput == "delete":
            print("Select a saved chat name to delete. THIS ACTION IS IRREVERSABLE!")
            userinput = input(">> ")
            if userinput in savedchats.keys():
                currentchatname = userinput
                savedchats.pop(currentchatname)
                saveData(savedchats)
                print("Removed!")
            else:
                print("That saved chat does not exist.")
        elif userinput == "model":
            changeModel()
        elif userinput == "help":
            print("Wow! Some cool help values.\nripoffcai requires the Ollama app AND the Python module.\nThe default model is gemma2:9b, you can change this in the script itself\n\n> is the first action input (e.g load, new)\n>> is a specification input (e.g chat names, character names etc)\n>>> is chatting to the character (or a slash command)\n->> is a past chat message\nyeah idk what else to write")
        elif userinput == "filesizes":
            tempthing = 0
            stringo = ""
            for index, value in savedchats.items():
                with open("temp.pkl", "wb") as file:
                    pickle.dump({index: value}, file)
                filestats = os.stat("temp.pkl")
                if tempthing == 0:
                    stringo = f"{index}: {(round(filestats.st_size / 1024 * 100)) / 100}kb"
                else:
                    stringo = stringo + f" | {index}: {(round(filestats.st_size / 1024 * 100)) / 100}kb"
                tempthing = tempthing + 1
                if tempthing == 3:
                    tempthing = 0
                    print(stringo)
                    stringo = ""
                os.remove("temp.pkl")
        elif userinput == "exit":
            print("Goodbye!")
            exit()
        else:
            print("That command does not exist.")

    print("Loading character...")

    if currentchatname == "":
        conversation_history = [
            {'role': 'user', 'content': prompt + characterinfo[characterchoice]["Definition"]}
        ]

        stream = ollama.chat(
            model=currentmodel,
            messages=conversation_history,
            stream=True,
        )
        print("")
        ai_response = ""
        for chunk in stream:
            ai_response += chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)
        conversation_history.append({'role': 'assistant', 'content': ai_response})
        print("\n")
    else:
        isfirstthing = True
        for item in conversation_history:
            if isfirstthing:
                isfirstthing = False
            else:
                print("")
                if item["role"] == "assistant":
                    print(item["content"])
                else:
                    print(f">>> {item['content']}")

    print("")

    # [ talk to character ]
    while True:
        userinput = input(">>> ")
        if len(userinput) > 0:
            if userinput[0] == "/":
                if userinput == "/exit":
                    del conversation_history
                    conversation_history = []
                    currentchatname = ""
                    break
                elif userinput == "/regenerate":
                    if len(conversation_history) > 2:
                        print(f"Regenerating response...\n\n->> {conversation_history[-2]['content']}\n")
                    else:
                        print("Regenerating response...")
                    del conversation_history[-1]
                    stream = ollama.chat(
                        model=currentmodel,
                        messages=conversation_history,
                        stream=True,
                    )
                    ai_response = ""
                    for chunk in stream:
                        ai_response += chunk['message']['content']
                        print(chunk['message']['content'], end='', flush=True)
                    conversation_history.append({'role': 'assistant', 'content': ai_response})
                    print("\n")
                elif userinput == "/back":
                    if len(conversation_history) > 2:
                        del conversation_history[-1]
                        del conversation_history[-1]
                        print(f"Went back to last response! Last messages:\n->> {conversation_history[-2]['content']}\n\n{conversation_history[-1]['content']}\n")
                    else:
                        print("you can't go back that far lol\n")
                elif userinput == "/save":
                    saveChat(False)
                elif userinput == "/saveas":
                    saveChat(True)
                elif userinput == "/model":
                    changeModel()
                elif userinput == "/?":
                    print("These are a list of commands:\n/regenerate - regenerates the last response\n/back - goes back to your last response\n/save - saves this chat\n/saveas - saves this chat but as a different name\n/model - changes ollama model\n/exit - exits this current chat (does not save data!)\n")
                else:
                    print(f"{userinput} is not a valid command.\n")
            else:
                try:
                    conversation_history.append({'role': 'user', 'content': userinput})
                except KeyboardInterrupt:
                    print(f"\n\nKeyboardInterrupt detected, went back\nLast messages:\n->> {conversation_history[-2]['content']}\n\n{conversation_history[-1]['content']}")
                try:
                    stream = ollama.chat(
                        model=currentmodel,
                        messages=conversation_history,
                        stream=True,
                    )

                    print("")
                    ai_response = ""
                    for chunk in stream:
                        ai_response += chunk['message']['content']
                        print(chunk['message']['content'], end='', flush=True)
                    conversation_history.append({'role': 'assistant', 'content': ai_response})
                except KeyboardInterrupt:
                    del conversation_history[-1]
                    print(f"\n\nKeyboardInterrupt detected, went back\nLast messages:\n->> {conversation_history[-2]['content']}\n\n{conversation_history[-1]['content']}")
                
                print("\n")
    
    del conversation_history
    conversation_history = []
    currentchatname = ""