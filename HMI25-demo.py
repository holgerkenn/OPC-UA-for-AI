# HMI 2025 Demo code
# Copyright (c) 2025 Holger Kenn
# MIT License, see LICENSE file for details

import paho.mqtt.client as mqtt
import gzip
import json
from langchain_ollama import ChatOllama

# this assumes that ollama is running locally and that this model is available. 
# probably a good idea to run the model from the ollama command line first to avoid the download and startup time.
llm = ChatOllama(
    model="deepseek-r1:1.5b"
)

from langchain_core.messages import AIMessage


#define some global variables where we collect the data from the received messages. 
fullmessage="" #collection of messages we will give to the LLM
metamessage="" #collection of metamessages
datamessage="" #collection of data messages
datamessagecount=0
metamessagecount=0
datadone=False
metadone=False

# Define the callback function for when a message is received
# as we don't know in which sequence the messages will arrive,
# we'll collect and count incoming messages depending on type and
# stop collecting once we have sufficient messages of each type
def on_message(client, userdata, msg):
    global datamessage
    global metamessage
    global datamessagecount
    global metamessagecount
    global datadone
    global metadone
    # Decode the MQTT message payload and decompress it in case it is gzipped
    compressed_data = msg.payload
    # TODO: format error handling
    if (compressed_data[0]==0x1f and compressed_data[1]==0x8B): # this is a cheap trick to recognize GZIP data content. Use with caution!
        decompressed_data = gzip.decompress(compressed_data)
        payload=decompressed_data.decode("utf-8")
    else:
        payload=compressed_data.decode("utf-8")
    parsed_data=json.loads(payload)
    if ('MessageType' in parsed_data.keys() ):
        mt=parsed_data['MessageType']
        if (mt=='ua-data' and not datadone):
            print(parsed_data)
            datamessage+=payload
            datamessagecount+=1
            if (datamessagecount >5): # there are 5 data sources contained in the stream of the demo application.
                datadone=True
        if (mt=='ua-metadata'and not metadone):
            print(parsed_data)
            metamessage+=payload
            metamessagecount+=1
            if (metamessagecount>5): # there are 5 meta messages in the stream of the demo application. 
                metadone=True


# Define the MQTT client
client = mqtt.Client()
# Connect to the MQTT broker, change as needed. This assumes a local mosquitto instance without SSL and without authentication
client.connect("localhost", 1883, 60)
client.on_message=on_message

# Subscribe to everything coming. 
client.subscribe("#")

# Start the network loop to process incoming messages, stop when sufficient messages have been received.
run=True
while run:
    rc = client.loop(timeout=5.0)
    if (datadone and metadone):
        run=False

fullmessage=metamessage+datamessage

print(fullmessage)

content=fullmessage + "  A pressure value is indicated by the text pascal in the description field. " # this is the place where additional message-specific text hints can be added as needed.

messages = [
    (
        "system",
        "You are a helpful assistant that answers questions about input data.",
    ),
    ("human", "here is the data in json format:" + content + " Here is the question: What is the last pressure of the Boiler at the Riverdale site?" ),
]
ai_msg = llm.invoke(messages)
print(ai_msg.content)
