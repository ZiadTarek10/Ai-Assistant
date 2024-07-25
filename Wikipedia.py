import wikipedia

def search_wikipedia(topic):
    try:
        result = wikipedia.summary(topic, sentences=5)
        return result
    except wikipedia.exceptions.DisambiguationError as e:
        return "It seems there are multiple options. Please be more specific."
    except wikipedia.exceptions.PageError as e:
        return "Sorry, I could not find any information on that topic."
    except Exception as e:
        return "An error occurred: " + str(e)
