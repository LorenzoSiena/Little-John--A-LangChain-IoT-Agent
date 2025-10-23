# LittleJohn A LangChain IoT Agent

A Python-based voice assistant project that processes voice commands and performs various actions, built with LangChain 1.0.

## Description

This project implements a voice-activated agent that can:
- Listen to voice commands
- Process natural language using LangChain 1.0
- Execute tasks based on voice input
- Control LED lights remotely through an included server (must be configured)

## Installation

```bash
#On your machine
git clone https://github.com/LorenzoSiena/Little-John--A-LangChain-IoT-Agent.git
cd Little-John--A-LangChain-IoT-Agent
uv sync
```

```bash
#On the api led server (Optional)
pip install microdot gpiozero 
```
## Usage
Run the Agent with the gui
```bash
uv run gui.py
```

The LED control server is included in the repository and can be started with:
```bash
python led_server_microdot_raspy.py
```
For this particular example, you need Microdot for the API server and gpiozero to control the LEDs,
which you can find [**here**](https://github.com/miguelgrinberg/microdot) and [**here**](https://github.com/gpiozero/gpiozero).


## Dependencies

- faster-whisper>=1.2.0
- gtts>=2.5.4
- langchain[google-genai]>=1.0.1
- langchain-google-vertexai>=3.0.0
- pygame>=2.6.1
- pynput>=1.8.1
- python-dotenv>=1.1.1
- sounddevice>=0.5.2

## Contributing

Feel free to submit issues and pull requests.

## License

[MIT License](LICENSE)

## Author

Lorenzo Siena

