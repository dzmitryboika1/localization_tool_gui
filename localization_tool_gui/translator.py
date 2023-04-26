import json
from pathlib import Path

from requests import HTTPError
import translators as ts


def translate(text, lang):
    """
    Translate text from one language to another. Language of the source string is determined automatically.
    It takes two positional arguments: text: str - source text; lang: str - language to translate
    Returns str - translated text. By default, the func uses Google translator. To get all available languages
    use ts.translators_pool. To get all available translators use official
    docs of package translators https://pypi.org/project/translators/
    """
    translated_text = ''
    try:
        translated_text = ts.translate_text(text, from_language='auto', to_language=lang, translator='google')
        return translated_text
    except HTTPError:
        print("HTTPError, try to use another translator in parameter translator")
        return translated_text


def localize_single_arb_file(file_path, output_dir, lang):
    """
    Function deserializes an .arb file translates all values into the required language.Next, it serializes the
    data back into the .arb file. It takes 3 positional arguments: arb_file_path: str - path to source .arb file;
    output_dir: str - dir where output .arb file will be saved; lang: str - target language to translate. Returns None
    """
    input_path = Path(file_path)
    file_name = input_path.stem
    if Path(file_path).is_file() and Path(file_path).suffix == '.arb':
        try:
            with open(file_path, encoding='utf-8') as file:
                text = file.read()
                # get list of tuples with key-value pairs from arb
                decoded_arb_file = json.loads(text, object_pairs_hook=list)
        except Exception as err:
            print(err)
        # get values from arb file and converse it to single string of values using line break for delimiter
        # it needs to send one request to translator API instead of many for each value"""
        values_str = '\n'.join([key_value[1] for key_value in decoded_arb_file])

        translated_values_list = translate(values_str, lang).split('\n')

        # collect output arb with translated values
        output_arb = {value[0]: translated_values_list[index] for index, value in enumerate(decoded_arb_file)}

        output_file_name = f'translated_{Path(file_name).stem}.arb'
        output_path = f'{output_dir}/{output_file_name}'

        with open(output_path, "w", encoding="utf-8") as write_file:
            json.dump(output_arb, write_file, ensure_ascii=False)


def multiple_arb_files_localization(input_dir, output_dir, lang):
    """
    Helper function for localize_single_arb_file for handling multiple .arb files. It takes 3 positional arguments:
    arb_file_path: str - path to source dir with .arb files; output_dir: str - dir where output .arb files will be
    saved; lang: str - target language to translate. Returns None
    """
    all_files = list(Path(input_dir).glob('*.arb'))

    for index, item in enumerate(all_files):
        localize_single_arb_file(item, output_dir, lang)
        print(f"Completed: {index + 1}/{len(all_files)}")