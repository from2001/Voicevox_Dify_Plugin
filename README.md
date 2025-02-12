# Voicevox dify plugin

## Overview
VOICEVOX DIFY Plugin is a TTS (Text-to-Speech) plugin for the Dify platform that integrates with VOICEVOX, a free Japanese voice synthesis engine. This plugin allows Dify applications to convert text into natural-sounding Japanese speech using various voice models. This plugin is compatible with Dify 1.x.

## Installation

Download `voicevox.difypkg` and install it selecting `Local Package File` in the Plugins section on your Dify console.

## Development

### Setup

#### At your local develop environment

1. Ensure you have Python 3.10+ installed
2. Install the required dependencies:
    ```sh
    pip install -r ./voicevox/requirements.txt
    ```
3. Copy .env.example to .env and configure:
    ```
    INSTALL_METHOD=remote
    REMOTE_INSTALL_HOST=locahost
    REMOTE_INSTALL_PORT=5003
    REMOTE_INSTALL_KEY=your_debug_key
    ```

Remote debugging information is available here.   
<img width="504" alt="debugging_info" src="https://github.com/user-attachments/assets/91347ffe-f3e9-4cb4-a20c-86ab35b20bdf" />

#### At your Dify server

1. If you get `plugin verification` error, set `FORCE_VERIFYING_SIGNATURE=false`. See more [details](https://github.com/langgenius/dify-docs/blob/main/en/learn-more/faq/plugins.md).

2. Install FFMpeg

This process is only required with v1.0.0-beta.1 since ffmpeg will be included in the newer version of docker-plugin_daemon docker image.
```sh
docker exec -it docker-plugin_daemon-1 apt-get update
docker exec -it docker-plugin_daemon-1 apt-get install -y ffmpeg
```


### Remote debugging

```sh
# Execute main.py on your local development environment.
cd voicevox
python main.py
```

Voicevox plugin will appear in debugging mode.   

<img width="1031" alt="voicevox_plugin" src="https://github.com/user-attachments/assets/ae25d18a-7457-456d-9aa8-4cb3ef9b09ab" />

### Packaging

#### Download Scaffolding Tool

Download the version suitable for your operating system. (dify-plugin-darwin-arm64 for Apple silicon mac). Put it in the root directory of this repository.
https://github.com/langgenius/dify-plugin-daemon/releases

```
chmod +x dify-plugin-darwin-arm64
```

### Pack into difypkg

```
./dify-plugin-darwin-arm64 plugin package ./voicevox
```
`voicevox.difypkg` will be generated.



## Acknowledgments
This project was inspired by and references code from the following sources:  

 - [dify-voicevox-tts](https://github.com/uezo/dify-voicevox-tts) by uezo
