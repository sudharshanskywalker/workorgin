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
        },

        'graphic_designer': {
            'keywords': ['graphic', 'design', 'logo', 'illustrat', 'photoshop', 'edit'],
            'response': "Creative project? 🎨 I've found talented graphic designers for you.",
            'action': {"type": "link", "url": "/services?q=graphic+designer", "label": "View Designers"}
        },

        'painter': {
            'keywords': ['paint', 'color', 'wall', 'brush'],
            'response': "Need a fresh coat of paint? 🖌️ I can link you with professional painters.",
            'action': {"type": "link", "url": "/services?q=painter", "label": "List Painters"}
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

        elif any(kw in user_message for kw in ['hello', 'hi', 'hey', 'hy']):
            response = "Hello Sir/Madam! I'm Jarvis, How can I help you today?"

        elif any(kw in user_message for kw in ['iam ambur asif', 'iam asif']):
            response = "Thalaivara ningala Anna, iam Jarvis anna , enna help vanam😉?"

        elif 'need' in user_message or 'find' in user_message:
            # Try to extract the search term
            parts = user_message.split('need')
            if len(parts) < 2: parts = user_message.split('find')
            
            if len(parts) >= 2:
                search_term = parts[1].strip().replace('a ', '').replace('an ', '')
                response = f"I'll help you find {search_term}! 🔍"
                action = {"type": "link", "url": f"/services?q={search_term}", "label": f"Search for {search_term}"}
            else:
                response = "What service are you looking for? (e.g., 'I need a plumber')"
        else:
            response = "I'm Jarvis! 🤖 Tell me what you need, for example: 'I need a graphic designer' or 'find me a painter'."

    return response, action