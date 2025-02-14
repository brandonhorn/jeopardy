from bs4 import BeautifulSoup
import pandas as pd
import re

def parse_html(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract categories
    categories = [cat.get_text() for cat in soup.select('.round .category .category_name')]

    # Initialize lists to store the data
    data = []

    # get the next game id and previous game id, from the achor tag with "showgame.php?game_id=" in the href
    game_anchors = soup.select_one('#contestants').find_all('a', href=re.compile(r'showgame.php\?game_id='))
    prev_game_id = game_anchors[0].get('href').split('=')[1]
    next_game_id = game_anchors[1].get('href').split('=')[1] if len(game_anchors) > 1 else None


    # Extract questions, values, and answers
    clues = soup.select('.round .clue')
    if len(clues) == 0:
        raise Exception('No clues found in the HTML content')
    for clue in clues:
        if clue.select_one('.clue_text') is None:
            continue
        question = clue.select_one('.clue_text').get_text(strip=True)
        clue_id = clue.select_one('.clue_text').get('id')
        match = re.search(r'clue_.+_(\d+)_\d+', clue_id)
        val_match = re.search(r'clue_.+_\d+_(\d+)', clue_id)
        category_index = match.group(1)
        # double jeopardy ids will contain 'DJ' in ID
        if 'DJ' in clue_id:
            value = 400 * int(val_match.group(1))
            category = categories[int(category_index) +5]
        else:
            value = 200 * int(val_match.group(1))
            category = categories[int(category_index) - 1]
        
        answer = clue.select_one('.clue_text + .clue_text em.correct_response').get_text(strip=True) if clue.select_one('.clue_text + .clue_text em.correct_response') else None
        data.append([category, question, value, answer])

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Category', 'Question', 'Value', 'Answer'])
    return (df, prev_game_id, next_game_id)

