def get_bot_response(user_message):

    user_message = user_message.lower()

    response = ""
    action = None

    intents = {
        'plumber': {
            'keywords': ['plumb', 'leak', 'pipe', 'tap', 'toilet', 'drain'],
            'response': "I'm JARVIS! 🤖 I've found several expert plumbers for you.",
            'action': {"type": "link", "url": "/services?q=plumber&location=&work_hours="}
        },

        'electrician': {
            'keywords': ['electr', 'wire', 'light', 'fan', 'switch', 'shock', 'power'],
            'response': "Power issues? ⚡ I can link you with electricians.",
            'action': {"type": "link", "url": "/services?category=home maintenance", "label": "List Electricians"}
        },

        'cleaning': {
            'keywords': ['clean', 'maid', 'sweep', 'wash', 'mop', 'housekeep'],
            'response': "Need a spotless home? 🧼 I've filtered the best cleaners.",
            'action': {"type": "link", "url": "/services?category=home services", "label": "List Cleaners"}
        },

        'carpenter': {
            'keywords': ['carpent', 'wood', 'furnitur', 'table', 'chair', 'door'],
            'response': "Working with wood? 🪵 I can find a skilled carpenter.",
            'action': {"type": "link", "url": "/services?category=carpentry", "label": "List Carpenters"}
        }
    }

    for intent in intents.values():
        if any(kw in user_message for kw in intent['keywords']):
            response = intent['response']
            action = intent['action']
            break

    if not response:
        if any(kw in user_message for kw in ['how', 'book', 'step']):
            response = "It's easy! 1️⃣ Search service 2️⃣ Pick a worker 3️⃣ Click Book Now 🚀"

        elif any(kw in user_message for kw in [ 'hello']):
            response = "Hello Sir/Madam! I'm  Jarvis, How can i help you?"

        elif any(kw in user_message for kw in ['hi']):
            response = "Hi Sir/Madam! I'm  Jarvis, How can i help you?"
        elif any(kw in user_message for kw in ['hy']):
            response = "Hy dude,! I'm  Jarvis, How can i help you😉?"
        elif any(kw in user_message for kw in ['iam ambur asif','iam asif']):
            response = "Thalaivara ningala Anna, iam Jarvis anna , enna help vanam😉?"



        else:
            response = "Tell what you need or help eg: i need a graphic designer."

    return response, action