# OPC UA for AI Demo

## Prerequisites

### Hardware

64 bit CPU (x64 or ARM), 8 GB RAM

The entire demo can be run on a single linux host including a Raspberry Pi 5 with 8GB memory

Optional: hardware acceleration for AI models, e.g. Nvidia CUDA, AMD ROCm 

Optional: OPC UA capable controllers as data source

### Software

-	OPC Foundation IIOT Starter kit https://github.com/OPCFoundation/UA-IIoT-StarterKit 

The starter kit assumes that you also install an MQTT broker such as Mosquitto https://mosquitto.org/ 
The starter kit is based on .net, 

-	ollama https://ollama.com/

ollama can use local acceleration hardware and multiple cores, make sure you install the right version.

To use ollama on the Raspberry Pi 5, the ARM64 version has been used.

- uv https://docs.astral.sh/uv/


## Install Instructions

1. Install .net

Use 64 bit ARM version of .net sdk, Version 9.0!
https://dotnet.microsoft.com/en-us/download/dotnet/9.0

The instructions assume that the .net tarfile has been downloaded into the $HOME directory

mkdir $HOME/dotnet-9
cd $HOME/dotnet-9
tar -zxvf ../dotnet-sdk-9.*-linux-arm64.tar.gz
export DOTNET_HOME=$HOME/dotnet-9
export PATH=$PATH/$HOME/dotnet-9

The IIOT SDK compiles some parts for .net 8, so while you're at it, also download version 8.0
https://dotnet.microsoft.com/en-us/download/dotnet/8.0

mkdir $HOME/dotnet-8
cd $HOME/dotnet-8
tar -zxvf ../dotnet-sdk-8.*-linux-arm64.tar.gz


2. Install mosquitto locally.
sudo apt update
sudo apt install mosquitto mosquitto-clients mosquitto-dev

sudo nano /etc/mosquitto/conf.d/local.conf
listener 1883
allow_anonymous true

(in the default install, mosquitto has persistence enabled. This will continuously write to your SD card, 
frying it in the process. You can disable persistence in the main mosquitto.conf file, but some mqtt clients
may take offence since they send QoS 1 or 2 which requires the mqtt broker to keep state. And thus write to disk.)

Disable persistence:
sudo nano /etc/mosquitto/conf.d/persistence.conf 
persistence false
autosave_interval 0
autosave_on_changes false

3. Download the IIOT SDK

mkdir src
cd src
git clone --recursive https://github.com/OPCFoundation/UA-IIoT-StarterKit.git

4. Start the build. And get a cup of coffee. or two...

cd UA-IIoT-StarterKit/
dotnet build ./UA-IIoT-StarterKit.sln

Open a second shell and run 'iostat 10', you will probably see a lot of %iowait. That's your SD card being abused.

5. Run the Publisher and the subscriber.
There seems to be a bug that running them actually requires .net 8 and not 9.

To run the publisher and subscriber with .net 8, change the DOTNET_HOME and PATH variables accordingly

There are two shell files run-publisher.sh and run-subscriber.sh that do this.

The SDK seems to be ok with persistence being disabled in mosquitto. 

6. install uv

curl -LsSf https://astral.sh/uv/install.sh | sh

7. Create a venv and install the required python packages

uv venv venv

source venv/bin/activate

uv pip install langchain-ollama
uv pip install paho-mqtt
uv pip install cryptography


8. check ollama

ollama run deepseek-r1:1.5b

Initially, this will download the model, so it may take some time.

Once the model is loaded, this should give you a '>>>' prompt, just type something, e.g. "Hello"

>>> hello
<think>

</think>

Hello! How can I assist you today? 😊

Quit the prompt with CTRL-D





