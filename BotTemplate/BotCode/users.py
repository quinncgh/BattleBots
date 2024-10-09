

class RealUser:
    def __init__(self):
        self.id = None
        self.tweet_count = 0
        self.z_score = 0
        self.username = None
        self.name = None
        self.description = None
        self.location = None
        self.posts = []

    def add_post(self, post):self.posts.append(post)


class RealPost:
    def __init__(self):
        # Variables for post data
        self.id = None
        self.text = None
        self.author_id = None
        self.created_at = None
        self.lang = None