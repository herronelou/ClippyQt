""" Convert ClippyJS agent.js to ClippyQT config """
import os
import re
import json
import ast
import base64


# Set this path to the directory containing the ffmpeg binary, used to convert audio resources
FFMPEG_EXECUTABLE = r'C:\Users\herro\Downloads\ffmpeg-6.0-full_build\ffmpeg-6.0-full_build\bin\ffmpeg.exe'


def convert_clippy_js_config(source, target, image_width):
    with open(source, 'r') as f:
        raw = f.read()

    # Convert to json
    trim_head = re.sub(r"^clippy\.ready\('[\S]+', ", '', raw)
    trim_tail = re.sub(r"\);$", '', trim_head)

    js_config = json.loads(trim_tail)
    sprite_width = js_config['framesize'][0]
    sprite_height = js_config['framesize'][1]

    for animation_name, animation in js_config['animations'].items():
        for frame in animation['frames']:
            print(frame)
            if 'images' in frame:
                # We need to convert the x/y offseets in "images" to a spriteIndex
                x_offset = frame['images'][0][0]
                y_offset = frame['images'][0][1]
                index = (x_offset // sprite_width) + (y_offset // sprite_height) * (image_width // sprite_width)
                frame['spriteIndex'] = index
                frame.pop('images')
            else:
                frame['spriteIndex'] = -1

    with open(target, 'w') as f:
        json.dump(js_config, f, indent=4)


def convert_audio_resources(source, target):
    """ Convert audio resources from ClippyJS (ogg stored in .js files) to .wav format compatible with QSound """
    with open(source, 'r') as f:
        raw = f.read()

    # Convert to json
    trim_head = re.sub(r"^clippy\.soundsReady\('[\S]+', ", '', raw)
    trim_tail = re.sub(r"\);$", '', trim_head)

    js_sounds = ast.literal_eval(trim_tail)

    for sound_name, sound in js_sounds.items():
        # Sound is a binary string, write it out to a temporary file
        temp_path = os.path.join(os.path.dirname(target), '{}.ogg'.format(sound_name))
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        # Convert str to base 64
        sound = sound.replace('data:audio/ogg;base64,', '')
        sound_bytes = base64.b64decode(sound.encode("ascii"))
        with open(temp_path, 'wb') as f:
            f.write(sound_bytes)
        # Convert to wav using ffmpeg
        wav_path = os.path.join(os.path.dirname(target), '{}.wav'.format(sound_name))
        ret = os.system('{} -i "{}" "{}"'.format(FFMPEG_EXECUTABLE, temp_path, wav_path))
        print('Converted {} to wav with return code {}'.format(sound_name, ret))
        # Remove the temp ogg file
        os.remove(temp_path)






if __name__ == '__main__':
    # convert_clippy_js_config(r'C:\Users\herro\repos\ClippyQt\agents\Clippy.js',
    #                          r'C:\Users\herro\repos\ClippyQt\agents\Clippy\config.json', 3348)
    convert_audio_resources(r'C:\Users\herro\Downloads\sounds-ogg.js',
                            r'C:\Users\herro\repos\ClippyQt\agents\Clippy\sounds')
