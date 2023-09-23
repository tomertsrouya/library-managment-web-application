import requests


def get_book_cover(title, api_key='AIzaSyC3JbIbLqZRw-zhRSF6aW5t9ihWZdyQEj8'):
    # Set the base URL
    base_url = 'https://www.googleapis.com/books/v1/volumes'

    # Set the search query and the number of results to retrieve
    query = title
    max_results = 1

    # Set the API parameters
    params = {
        'q': query,
        'maxResults': max_results,
        'key': api_key
    }

    # Make the API request
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return None

    # Get the book cover image URL from the API response
    data = response.json()
    if data['items'] == 0:
        return None
    try:
        book_cover_url = data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    except KeyError or ValueError:
        return None
    return book_cover_url


def get_book_information(book_title, author_name, api_key='AIzaSyC3JbIbLqZRw-zhRSF6aW5t9ihWZdyQEj8'):
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}+inauthor:{author_name}&key={api_key}"
    # Make the API request
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if data["totalItems"] == 0:
        return None
    try:
        # Get the relevant data from the API response
        book_description = data["items"][0]["volumeInfo"]["description"]
        publisher = data['items'][0]['volumeInfo']['publisher']
        publish_date = data['items'][0]['volumeInfo']['publishedDate'][:4]
        author = data['items'][0]['volumeInfo']['authors']
    except KeyError or ValueError:
        return None
    return book_description, publisher, publish_date, author

