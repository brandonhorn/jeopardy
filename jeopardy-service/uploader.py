import requests
from index_settings import IndexSettings

from parser import parse_html
from sql import sql_client


def get_html(index):
    game_url = f'https://j-archive.com/showgame.php?game_id={index}'
    response = requests.get(game_url)
    if response.status_code == 200:
        try:
            return parse_html(response.text)
        except Exception as e:
            print(f"Error parsing HTML content: {e}")
            return (None, None, None)
    return (None, None, None)

def upload_next(sql_client: sql_client, settings: IndexSettings, max_episodes):
    count = 0
    highest_index = settings.get_highest_index()
    lowest_index = settings.get_lowest_index()
    question_count = settings.get_question_count()
    next_id = settings.get_next_id()

    if next_id is None:
        (_, _, next_id) = get_html(highest_index)
    
    if next_id is None:
        print("No more episodes to upload. Exiting...")
        return

    while count < max_episodes:
        if next_id is None:
            print("No more episodes to upload. Exiting...")
            return
        temp_high = next_id
        (df, _, next_id) = get_html(next_id)
        if df is None:
            settings.update_settings(highest_index, lowest_index, question_count, settings.get_prev_id(), next_id)
            print(f"No more episodes to upload. Exiting")
            return
        highest_index = temp_high
        # add a column continuing the index, starting from the current question count
        df['Index'] = range(question_count, question_count + len(df))
        question_count += len(df)
        sql_client.upload(df)
        settings.update_settings(highest_index, lowest_index, question_count, settings.get_prev_id(), next_id)
        count += 1

def upload_prev(sql_client: sql_client, settings: IndexSettings, max_episodes):
    count = 0
    highest_index = settings.get_highest_index()
    lowest_index = settings.get_lowest_index()
    question_count = settings.get_question_count()
    prev_id = settings.get_prev_id()
    next_id = settings.get_next_id()

    if prev_id is None:
        (_, prev_id, _) = get_html(lowest_index)
    if prev_id is None:
        print("No more episodes to upload. Exiting...")
        return
    while count < max_episodes:
        if prev_id is None:
            print("No more episodes to upload. Exiting...")
            return
        temp_low = prev_id
        (df, prev_id, _) = get_html(prev_id)
        if df is None:
            settings.update_settings(highest_index, lowest_index, question_count, prev_id, next_id)
            print(f"No more episodes to upload. Exiting")
            return
        lowest_index = temp_low
        # add a column continuing the index, starting from the current question count
        df['Index'] = range(question_count, question_count + len(df))
        question_count += len(df)
        sql_client.upload(df)
        settings.update_settings(highest_index, lowest_index, question_count, prev_id, next_id)
        count += 1



def main(settings: IndexSettings):

    # Extract the highest index from the settings
    highest_index = settings.get('highest_read', 0)
    question_count = settings.get('question_count', 0)

    # Check if the page exists
    html_content = get_html(settings.get_highest_index+ 1)
    print(f"Fetching page {highest_index + 1}")

    if html_content:
        (df, prev_id, next_id) = parse_html(html_content)
        print(df)
        print(f"Prev ID: {prev_id}, Next ID: {next_id}")
        # upload(df, )
        print("Page exists and HTML content fetched.")
    else:
        print("Page does not exist.")

if __name__ == "__main__":
    main()