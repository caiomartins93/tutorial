"""Visualizing Twitter Sentiment Across America"""

from data import word_sentiments, load_tweets
from datetime import datetime
from doctest import run_docstring_examples
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait, message
from string import ascii_letters
from ucb import main, trace, interact, log_current_line


# Phase 1: The Feelings in Tweets

def make_tweet(text, time, lat, lon): #problema 1
    """Return a tweet, represented as a python dictionary.

    text      -- A string; the text of the tweet, all in lowercase
    time      -- A datetime object; the time that the tweet was posted
    latitude  -- A number; the latitude of the tweet's location
    longitude -- A number; the longitude of the tweet's location

    >>> t = make_tweet("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_words(t)
    ['just', 'ate', 'lunch']
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    """

    tweet = {'text': text, 'time': time, 'latitude': lat, 'longitude': lon}
    return tweet

def tweet_words(tweet): #problema 1
    """Return a list of the words in the text of a tweet."""
    return extract_words(tweet['text'])

def tweet_time(tweet): #problema1
    """Return the datetime that represents when the tweet was posted."""
    return tweet['time']

def tweet_location(tweet): #problema2
    """Return a position (see geo.py) that represents the tweet's location."""
    lat = tweet['latitude']
    lon = tweet['longitude']
    return make_position(lat, lon)

def tweet_string(tweet):
    """Return a string representing the tweet."""
    return '"{0}" @ {1}'.format(tweet['text'], tweet_location(tweet))

def check_if_alphabetic(charac): #problema3
    #if (ord(charac) > 96 and ord(charac)  < 123):
    if charac in ascii_letters:
        return True
    else:
        return False

def extract_words(text): #problema3
    """
    Return the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    """
    text = [text]
    for charac_position in range(0, len(text)):
        i = 0
        while i < (len(text[charac_position])):
            if check_if_alphabetic(text[charac_position][i]) == True:
                i += 1
            else:
                text[charac_position] = text[charac_position].replace(text[charac_position][i]," ")
                i += 1

    for charac_position in range(0, len(text)):
        text = text[charac_position].split()

    return text #retorna uma lista de palavras sem pontuacao


def make_sentiment(value): #problema4
    """Return a sentiment, which represents a value that may not exist.

    >>> s = make_sentiment(0.2)
    >>> t = make_sentiment(None)
    >>> has_sentiment(s)
    True
    >>> has_sentiment(t)
    False
    >>> sentiment_value(s)
    0.2
    """
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'
    s = value
    return s #retorna o valor do sentimento

def has_sentiment(s): #problema4
    """Return whether sentiment s has a value."""
    if s == None:
        return False
    elif s >= -1 and s <= 1:
        return True
    else:
        return False

def sentiment_value(s): # checa se há valor ou nao (None)
    """Return the value of a sentiment s."""
    assert has_sentiment(s), 'No sentiment value'
    if has_sentiment(s) == True:
        return s
    else:
        return None

def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word, if word is not in the sentiment dictionary.

    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    return make_sentiment(word_sentiments.get(word, None))


def analyze_tweet_sentiment(tweet): #problema5
    """ Return a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.

    If no words in the tweet have a sentiment value, return
    make_sentiment(None).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """
    word_list = tweet_words(tweet)
    words_with_sentiment = []
    for word in word_list:
        feeling = get_word_sentiment(word)
        if has_sentiment(feeling) == True:
            if feeling >= -1 and feeling <= 1:
                words_with_sentiment.append(feeling)
            else:
                pass
    if len(words_with_sentiment) > 0:
        return get_average(words_with_sentiment)
    else:
        return make_sentiment(None)

def get_average(all_sentiments):
    soma = 0
    for x in all_sentiments:
        soma = soma + x

    average = (soma / len(all_sentiments))
    return average


# Phase 2: The Geometry of Maps

def polygon_area(polygon): #problema6
#polygon == lista de tuplas [(lat_1, lon_1), (lat_2, lon_2)] dos vertices do poligono
    somatorio = 0
    for i in range(0, len(polygon) -1): # p/ cada tupla: posicao 0 == x E posi [1] == y
        somatorio += (polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1])
    area = 0.5 * somatorio
    return area

def find_centroid(polygon): #problema6
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p3, p2, p1])
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p2, p1])
    (1, 2, 0)
    """
    if polygon_area(polygon) == 0:
        return (polygon[0][0], polygon[0][1], 0)
    else:
        somatorioX = 0
        for i in range(0, len(polygon) -1):
            somatorioX += ((polygon[i][0] + polygon[i+1][0]) * ((polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1])))

        somatorioY = 0
        for i in range(0, len(polygon) -1):
            somatorioY += ((polygon[i][1] + polygon[i+1][1]) * ((polygon[i][0] * polygon[i+1][1]) - (polygon[i+1][0] * polygon[i][1])))

        Cx = (1/(6 * polygon_area(polygon))) * somatorioX
        Cy = (1/(6 * polygon_area(polygon))) * somatorioY

        return (Cx, Cy, abs(polygon_area(polygon))) #retorna coordenadas(lat e lon) do centroid do poligono e area


def find_center(polygons): #problema7
    """Compute the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    "*** YOUR CODE HERE ***"
    total_area = 0
    soma_centroide_area_x = 0
    soma_centroide_area_y = 0
    for polygon in polygons:
        C = find_centroid(polygon)
        soma_centroide_area_x += C[0] * C[2]
        soma_centroide_area_y += C[1] * C[2]
        total_area += C[2]
    centerXY = ((soma_centroide_area_x/total_area), (soma_centroide_area_y/total_area))
    return centerXY


# Phase 3: The Mood of the Nation

def find_closest_state(tweet, state_centers): #problema8
    """Return the name of the state closest to the given tweet's location.

    Use the geo_distance function (already provided) to calculate distance
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a dictionary from state names to positions.

    >>> us_centers = {n: find_center(s) for n, s in us_states.items()}
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
    "*** YOUR CODE HERE ***"
    tweet_location = make_position(tweet['latitude'], tweet['longitude'])
    estados = []
    for key in us_states:
        estados.append((key, geo_distance(tweet_location, find_center(us_states[key]))))
    for x in range(0, len(estados) -1):
        if estados[x][1] < estados[x+1][1]:
            estados[x], estados[x+1] = estados[x+1], estados[x]
    return estados[len(estados) -1][0]


def group_tweets_by_state(tweets): #problema9
    """Return a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> ca_tweets = group_tweets_by_state([sf, ny])['CA']
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    """
    tweets_by_state = {}
    all_states = []
    for x in tweets:
        all_states.append(find_closest_state(x, us_states))

    for y in all_states:
        tweets_by_state[y] = []

    for z in tweets:
        tweets_by_state[find_closest_state(z, us_states)].append(z)
    return tweets_by_state


def most_talkative_state(term): #problema10
    """Return the state that has the largest number of tweets containing term.

    >>> most_talkative_state('texas')
    'TX'
    >>> most_talkative_state('sandwich')
    'NJ'
    """
    tweets = load_tweets(make_tweet, term)  # A list of tweets containing term
    all_tweets = group_tweets_by_state(tweets) #retorna dic com todos os tweets por estado
    all_tweets_list = []
    for key in all_tweets:
        all_tweets_list.append((key, all_tweets[key]))

    for x in range(0, len(all_tweets) -1):
        if len(all_tweets_list[x][1]) > len(all_tweets_list[x+1][1]):
            most_talkative = all_tweets_list[x][0]
            all_tweets_list[x], all_tweets_list[x+1] = all_tweets_list[x+1], all_tweets_list[x]
        else:
            most_talkative = all_tweets_list[x+1]

    return most_talkative


def average_sentiments(tweets_by_state): #problema11
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets
    """
    averaged_state_sentiments = {}
    for state in tweets_by_state:
        state_sentiments = []
        for tweet in tweets_by_state[state]:
            sentiment = analyze_tweet_sentiment(tweet)
            if sentiment != None:
                state_sentiments.append(sentiment)

        if len(state_sentiments) != 0:
            averaged_state_sentiments[state] = get_average(state_sentiments)

    return averaged_state_sentiments


# Phase 4: Into the Fourth Dimension

def group_tweets_by_hour(tweets): #problema12
    """Return a dictionary that groups tweets by the hour they were posted.

    The keys of the returned dictionary are the integers 0 through 23.

    The values are lists of tweets, where tweets_by_hour[i] is the list of all
    tweets that were posted between hour i and hour i + 1. Hour 0 refers to
    midnight, while hour 23 refers to 11:00PM.

    To get started, read the Python Library documentation for datetime objects:
    http://docs.python.org/py3k/library/datetime.html#datetime.datetime

    tweets -- A list of tweets to be grouped
    """
    tweets_by_hour = {}
    for x in range(24):
        tweets_by_hour[x] = []

    for tweet in tweets:
        time = tweet_time(tweet)
        tweet_hour = time.hour
        tweets_by_hour[tweet_hour].append(tweet)

    return tweets_by_hour


# Interaction.  You don't need to read this section of the program.

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores."""
    words = extract_words(text.lower())
    assert words, 'No words extracted from "' + text + '"'
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1:+}'
    for word in extract_words(text.lower()):
        s = get_word_sentiment(word)
        if has_sentiment(s):
            print(layout.format(word, sentiment_value(s)))

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state."""
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    center = us_centers[center_state.upper()]
    dist_from_center = lambda name: geo_distance(center, us_centers[name])
    for name in sorted(us_states.keys(), key=dist_from_center)[:int(n)]:
        draw_state(us_states[name])
        draw_name(name, us_centers[name])
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()

def draw_state_sentiments(state_sentiments={}):
    """Draw all U.S. states in colors corresponding to their sentiment value.

    Unknown state names are ignored; states without values are colored grey.

    state_sentiments -- A dictionary from state strings to sentiment values
    """
    for name, shapes in us_states.items():
        sentiment = state_sentiments.get(name, None)
        draw_state(shapes, sentiment)
    for name, shapes in us_states.items():
        center = find_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_term(term='my job'):
    """Draw the sentiment map corresponding to the tweets that contain term.

    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        s = analyze_tweet_sentiment(tweet)
        if has_sentiment(s):
            draw_dot(tweet_location(tweet), sentiment_value(s))
    wait()

def draw_map_by_hour(term='my job', pause=0.5):
    """Draw the sentiment map for tweets that match term, for each hour."""
    tweets = load_tweets(make_tweet, term)
    tweets_by_hour = group_tweets_by_hour(tweets)

    for hour in range(24):
        current_tweets = tweets_by_hour.get(hour, [])
        tweets_by_state = group_tweets_by_state(current_tweets)
        state_sentiments = average_sentiments(tweets_by_state)
        draw_state_sentiments(state_sentiments)
        message("{0:02}:00-{0:02}:59".format(hour))
        wait(pause)

def run_doctests(names):
    """Run verbose doctests for all functions in space-separated names."""
    g = globals()
    errors = []
    for name in names.split():
        if name not in g:
            print("No function named " + name)
        else:
            if run_docstring_examples(g[name], g, True) is not None:
                errors.append(name)
    if len(errors) == 0:
        print("Test passed.")
    else:
        print("Error(s) found in: " + ', '.join(errors))

@main
def run(*args):
    """Read command-line arguments and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Trends")
    parser.add_argument('--print_sentiment', '-p', action='store_true')
    parser.add_argument('--run_doctests', '-t', action='store_true')
    parser.add_argument('--draw_centered_map', '-d', action='store_true')
    parser.add_argument('--draw_map_for_term', '-m', action='store_true')
    parser.add_argument('--draw_map_by_hour', '-b', action='store_true')
    parser.add_argument('text', metavar='T', type=str, nargs='*',
                        help='Text to process')
    args = parser.parse_args()
    for name, execute in args.__dict__.items():
        if name != 'text' and execute:
            globals()[name](' '.join(args.text))
