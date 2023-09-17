# Soundstorm: A Comprehensive Audio & AI Experience

## Overview

Soundstorm is a cutting-edge audio and AI Python application designed to provide a rich yet simplified experience for sound designers, algorithmic composers, and experimental audio enthusiasts. From sample pack creation and algorithmic composition to AI-powered chat features, Soundstorm is a sonic powerhouse. 

### Features

- 🎵 **AI Text-to-Audio Generation**: Generate any song or sound you want by a simple text prompt.
- 📦 **Algorithmic Sample Pack Creation**: Automatically generate sample packs based on user-defined criteria.
- 🎛 **Audio Effects**: Real-time audio effects like reverb, distortion, and more.
- 🎶 **Algorithmic Composition**: Create algorithmic composition.
- 🎹 **MIDI Randomizer**: Generate random MIDI sequences for creative inspiration.
- 🗨️ **Chat with GPT**: Integrated chat using OpenAI's GPT models for real-time conversational experiences.
- 🎲 **GPT Randomizer**: Generate random text snippets, prompts, or even song lyrics.


Please note: this is currently a prototype with a super stripped-down GUI and, while functional, can be buggy and does require finagling.

## Installation

### Prerequisites

- Python 3.11

### Install Dependencies

Clone the repository and navigate into the project directory. Run the following command to install all the necessary packages:

```bash
pip install pedalboard pydub replicate midiutil soundfile openai numpy
```

### API Keys

You'll need to have API keys for both Replicate and OpenAI:

- For Replicate, sign up at: https://replicate.com and follow the instructions to get your API key.
- For OpenAI, sign up at: https://openai.com/product and follow the instructions to get your API key.

Add these keys in the appropriate sections within the application before running it.

### Running the Application

After installing the prerequisites and obtaining the API keys, you can run the application using:

```bash
python Soundstorm.py
```

### Important

This is SUPER rough. Currently, it only exists as a Python script and has only been tested on 2 different Macs.

## Contributing

Contributions are welcome! This is the work of an amateur. Would love to see it fleshed out!

## Support

For support and feature requests, please open an issue on this repository.

[![Support via PayPal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.me/noodlebake)

## License

This project is licensed under the MIT License.


