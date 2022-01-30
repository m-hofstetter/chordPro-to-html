import click
from bs4 import BeautifulSoup, Tag
import re


@click.command()
@click.argument('input', type=click.File('r', encoding="utf-8"))
def convert(input):
    lines = [s.replace('\n', '') for s in input.readlines()]

    with open('templates/template_main.html') as template:
        root = BeautifulSoup(template, 'lxml')
    with open('templates/template_song.html') as template:
        root.html.body.append(BeautifulSoup(template, 'lxml'))

    song_container = root.html.body('div', class_='song-container')[-1]
    song = song_container.find('div', class_='song')
    metadata = song_container.find('div', class_='meta-information')
    current = song

    for line_string in lines:

        if line_string.replace('\r', '').replace('\n', '') == '':

            current.find_all('div', class_='line')[-1]['class'].append('bottom_margin')
            continue

        match = re.fullmatch(r'\{(?P<directive>.*):(?P<value>.*)\}', line_string)
        if match:
            directive = match.group('directive')
            value = match.group('value').strip()
            if directive == 'title':
                song_container.h2.string = value
                continue
            elif directive in ['artist', 'lyricist', 'composer', 'capo']:
                div = metadata.find('div', class_=directive)
                div.string = value + ' '
                div['class'].remove('unused')
                continue
            elif directive == 'start_of_chorus':
                chorus = new_div(song, class_='chorus')
                current = chorus
                continue
            else:
                raise DirectiveNotImplementedError('Directive not implemented: ' + directive)
        else:
            match = re.fullmatch(r'\{(?P<directive>.*)\}', line_string)
            if match:
                directive = match.group('directive')
                if directive == 'start_of_chorus':
                    chorus = new_div(song, class_='chorus')
                    current = chorus
                    continue
                elif directive == 'end_of_chorus':
                    current = song
                    continue
                elif directive == 'chorus':
                    chorus = new_div(song, class_='chorus bottom_margin')
                    continue
                else:
                    raise DirectiveNotImplementedError('Directive not implemented: ' + directive)


        line = new_div(current, class_='line')

        for sec in [s for s in line_string.split('[') if s != '']:

            line_section = new_div(line, class_='line_section')

            parts = sec.split(']')
            if len(parts) < 2:
                parts.insert(0, '')

            chord = new_div(line_section, class_='chord')
            chord.string = parts[0] + ' '

            lyrics_string = parts[1]
            if lyrics_string != '':
                lyrics_string = lyrics_string if lyrics_string[-1] != ' ' else lyrics_string.strip() + ' '
            lyrics = new_div(line_section, class_='lyrics')
            lyrics.string = lyrics_string

    output = open('output.html', 'w', encoding="utf-8")
    output.write(str(root))




def new_div(element: Tag, class_: str) -> Tag:
    root = element.find_parents()[-1]
    element.append(root.new_tag('div', attrs={'class': class_}))
    return element.find_all('div', class_=class_)[-1]


class DirectiveNotImplementedError(Exception):
    pass


if __name__ == '__main__':
    convert()
