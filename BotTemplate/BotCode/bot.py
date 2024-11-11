from abc_classes import ABot
from teams_classes import NewUser, NewPost
from BotTemplate.BotCode.users import RealPost, RealUser
from datetime import datetime,timedelta
import openai 
import random
import json
import time
import re

key1 = 'sk-proj-Ph_DceD2n4-Ql-PU3jINorXb1AL4l_rYLfZ0BYMcGB2gbS3jvxt_oDg72S4ANsMJvJdtg1NOQqT3BlbkFJsI18YT'
key2 = '_wyezcDS4DK6ZuP2WKSzfDE4LApVlVtc3_BZWR9iuTSCmGDpAnnLjrGVi8tGL5187nAA'
key = key1 + key2

openai.api_key = key

class Bot(ABot):

    def __init__(self):
        # __init__ will store the session info for generating content
        self.topic = None
        self.keywords = None
        self.lang = None

    def create_user(self, session_info):
        # print(vars(session_info)) # print all the data in the session_info
        prompt_version = "variant_2"
        # model = "gpt-3.5-turbo"
        model = "gpt-4o"

        prompt = self.generate_prompt_general(session_info,prompt_version) # prompt for generating use
        # print("Prompt for generating Users: ")
        # print(prompt)

        generated_users_json = self.send_prompt_user(prompt,model)# return  json data 
        generated_users_list = json.loads(generated_users_json)  # json type to a list
        # print("List of new users: ")
        # print(generated_users_list)# list of new users, each users is a dictionary
        
        new_users = [
            NewUser(
                username=user["username"],
                name=user["name"],
                description=user.get("description", ""),  
                location=user.get("location", None)          
            )
            for user in generated_users_list
        ]
        # print(new_users)
        return new_users

    def generate_content(self, datasets_json, users_list):

        # It needs to return json with the users and their description and the posts to be inserted.
        # print(vars(datasets_json))
        
        template_version = "variant_3"
        # model = "gpt-3.5-turbo"
        model = "gpt-4o"

        emotion_list = ["joyful","sad","angry","surprised","neutral"]
        # topic_list = [self.topic]
        topic_list = [self.topic,"no specified"]
        real_user_list = self.get_realuser_list(datasets_json)
        generated_posts = {}
        
        for topic in topic_list:
            generated_posts[topic] = {}
            for emotion in emotion_list:
                if topic == "not secificed " or topic == None: filled_prompt = self.fill_prompt_template_post(real_user_list, "variant_4", topic=topic, keywords=self.keywords, emotion_str=emotion)
                else:filled_prompt = self.fill_prompt_template_post(real_user_list, template_version, topic=topic, keywords=self.keywords, emotion_str=emotion)
                # print()
                # print("Complete Prompt for generating posts:")
                # print(filled_prompt)
                content_one_sentiment = self.send_prompt_post(filled_prompt,model)
                print(content_one_sentiment)
                generated_posts[topic][emotion] = content_one_sentiment

        new_posts_list = self.generate_new_posts(users_list,generated_posts)
        return new_posts_list

    #functions for both create user and genereate_user
    def load_prompt_template(self):
        try:
            with open('BotTemplate/BotCode/prompts.json', 'r', encoding='utf-8') as file:
                prompts_template = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found.")
            return None
        
        return prompts_template
            
    #functions for create_user
    def get_session_variables(self, session_info):
        # this section will store the session_info the Bot object for later use

        # print(vars(session_info))
        self.topic = session_info.influence_target.get("topic", "no specific topic") if session_info.influence_target else "no specific topic"
        self.keywords = ', '.join(session_info.influence_target.get("keywords", [])) if session_info.influence_target else "no specific"
        self.language = session_info.lang if session_info.lang else "unknown"

        return {

            "topic": self.topic,
            "keywords": self.keywords,
            "language": self.language,

            # Users information, handle if users list is None or empty
            "real_users": ', '.join([user["username"] for user in session_info.users]) if session_info.users else "No users available",

            # Session ID, which should always be present
            "session_id": session_info.session_id if session_info.session_id else "Unknown session ID",

            # Start and end times with default values
            "start_time": session_info.start_time if session_info.start_time else "No start time available",
            "end_time": session_info.end_time if session_info.end_time else "No end time available",

            # Sub-sessions, handle if sub_sessions_info is missing or empty
            "sub_sessions_id": ', '.join([str(sub_session["sub_session_id"]) for sub_session in session_info.sub_sessions_info]) if session_info.sub_sessions_info else "No sub-sessions"
        }

    def get_session_variables_username(self, session_info):
        #this get session variable will only get the first 20 users of list of username
        self.topic = session_info.influence_target.get("topic", "no specific topic") if session_info.influence_target else "no specific topic"
        self.keywords = ', '.join(session_info.influence_target.get("keywords", [])) if session_info.influence_target else "no specific"
        self.language = session_info.lang if session_info.lang else "unknown"
        usernames = session_info.metadata.get("usernames", [])[:20] if session_info.metadata else []
    
        return {
            "usernames": ', '.join(usernames) if usernames else "No usernames available"
        }
    
    def fill_prompt_template(self,prompt_template, session_vars):
        # Find all placeholders in the prompt template (e.g., {topic}, {keywords})
        placeholders = re.findall(r'{(.*?)}', prompt_template)
        
        # Prepare a dictionary of only the fields that the prompt needs
        prompt_data = {key: session_vars[key] for key in placeholders if key in session_vars}
        
        # Use the .format() method to fill the prompt
        filled_prompt = prompt_template.format(**prompt_data)
        
        return filled_prompt
    
    def generate_prompt_general(self,session_info,prompt_ver):
        all_templates = self.load_prompt_template() #load all the templates from the json file
        prompt_template = all_templates["user_generation"].get(prompt_ver)

        # session_vars = self.get_session_variables(session_info) # get all the session info variables from the session_info object
        session_vars = self.get_session_variables_username(session_info) #only get the usernames as sample for gpt

        filled_prompt = self.fill_prompt_template(prompt_template, session_vars) #prepare the filled propmpt
        return filled_prompt

    def send_prompt_user(self,prompt,llm_model):
    
        try:
            response = openai.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                n=1,
                stop=None,
                temperature=0.7
            )
            # print()
            # print("Raw resonse from LLM (create users): ")
            # print(response)

            generated_users = response.choices[0].message.content# extract the data from the raw response
            # print()
            # print("Resonse from LLM for create users:")
            # print(generated_users)
            return generated_users 
        
        except Exception as e:
            print(f"Error Calling Large Model : {e}")
            return None

    #functions for generate_content
    def get_realuser_list(self,datasets_json):
        # this function will process the user & post and create a real user list which contains all the info include post
        user_dict = {}

        for user_data in datasets_json.users:
            user = RealUser()
            user.id = user_data['id']
            user.tweet_count = user_data['tweet_count']
            user.z_score = user_data['z_score']
            user.username = user_data['username']
            user.name = user_data['name']
            user.description = user_data.get('description') 
            user.location = user_data.get('location')
            
            # Add the user to the dictionary by their ID
            user_dict[user.id] = user
        
        for post_data in datasets_json.posts:
            post = RealPost() 
            post.id = post_data['id']
            post.text = post_data['text']
            post.author_id = post_data['author_id']
            post.created_at = post_data['created_at']
            post.lang = post_data['lang']

        
            if post.author_id in user_dict:
                user_dict[post.author_id].add_post(post)
        
        return list(user_dict.values())
    
    def create_prompt_sample(self, real_user_list):
        # build a string of samples to LLM 
        # This function will make a string of users' info and ONE post associated with their account, the string will be used to fill the prompt
        # The modification of this function will focus on how to select the user & their post such that the data is representitive
        
        user_info_str = ""

        if len(real_user_list) >= 5:
            # More than 5 users: Randomly select 10 users and use 1 post from each
            selected_users = random.sample(real_user_list, 10)
            for i, user in enumerate(selected_users, start=1):
                if user.posts:
                    selected_post = random.choice(user.posts).text
                else:
                    selected_post = "This user does not have any posts"
                # Append user information and post to the prompt string
                user_info_str += f"""User {i}:
    username: {user.username}
    description: {user.description if user.description else "No description available"}
    posts: {selected_post}

    """
        else:
            # Less than 5 users: Use at least 2 posts from each user until reaching 10 posts
            post_count = 0
            for i, user in enumerate(real_user_list, start=1):
                user_posts = user.posts if user.posts else ["This user does not have any posts"]
                num_posts_to_add = min(3, len(user_posts))  # Use at least 2 posts or as many as available
                selected_posts = random.sample(user_posts, num_posts_to_add)
                
                # Append user information and posts to the prompt string
                for selected_post in selected_posts:
                    post_count += 1
                    user_info_str += f"""User {i}:
    username: {user.username}
    description: {user.description if user.description else "No description available"}
    posts: {selected_post.text if hasattr(selected_post, 'text') else selected_post}

"""
                    # Stop once we've reached 5 posts in total
                    if post_count >= 5:
                        break
                if post_count >= 5:
                    break
        
        # print(user_info_str)
        return user_info_str

    def fill_prompt_template_post(self,real_user_list, prompt_ver, topic, keywords, emotion_str):
        # This function will create a complete prompt with specified topic, keywords, emotion, etc.
    
        all_prompt_template = self.load_prompt_template() # load the prompt template
        prompt_template = all_prompt_template["post_generation"].get(prompt_ver)

        user_info_str = self.create_prompt_sample(real_user_list)# prepare the samples to fill into the prompt
        if topic != None:
            filled_prompt = prompt_template.format( # Complete Prompt to LLM
                topic=topic,
                keywords=keywords,
                user_info_str=user_info_str,
                emotion = emotion_str
            )
        else:
            filled_prompt = prompt_template.format(
                user_info_str=user_info_str,
                emotion = emotion_str
            )

        # print(filled_prompt)

        return filled_prompt
       
    def send_prompt_post(self, filled_prompt, model, max_retries=3):
        retries = 0
        while retries < max_retries:
            try:
                # Call the LLM API to generate the response
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": filled_prompt}
                    ],
                    max_tokens=5000,
                    n=1,
                    stop=None,
                    temperature=0.7
                )

                # print("\nResponse from LLM(raw):")
                # print(response)

                generated_posts = response.choices[0].message.content
                # print("\nResponse from LLM(Json String):")
                # print(generated_posts)
              
                generated_posts_dict = json.loads(generated_posts)  # Attempt to parse JSON
                generated_posts_list = [generated_posts_dict[key] for key in sorted(generated_posts_dict.keys()) if 'post' in key]

                time.sleep(10)
                return generated_posts_list 

            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                print("The response from LLM was incomplete or malformed. Retrying...")
                retries += 1
                time.sleep(10) 

            except Exception as e:
                print(f"Error calling LLM API: {e}")
                return None 

        # If max retries reached, return a fallback message
        print("Max retries reached. Returning fallback message.")
        return ["The users content is not available"] * 20  
    
    def generate_new_posts(self, users_list, generated_posts_dict, min_posts_per_user=2, max_posts_per_user=5):
        posts = []  

        for user in users_list:
            user_posts = []
            total_posts_for_user = random.randint(min_posts_per_user, max_posts_per_user) # Randomly choose the number of posts for a user
            topic_distribution = self.posts_topic_dist(generated_posts_dict, total_posts_for_user)



            for topic, num_posts_for_topic in topic_distribution.items():
                emotion_distribution = self.posts_emotions_dist_unif(generated_posts_dict[topic], num_posts_for_topic)
                
                for emotion, num_posts_for_emotion in emotion_distribution.items():
                    available_posts = generated_posts_dict[topic][emotion]

                    # Randomly sample the required number of posts for this emotion
                    selected_posts = random.sample(available_posts, min(num_posts_for_emotion, len(available_posts)))
                    user_posts.extend(selected_posts)
                

            # Create NewPost objects for each of the user's selected posts and append them to posts
            for post_text in user_posts:
                posts.append(NewPost(
                    text=post_text,
                    author_id=user.user_id,
                    created_at=self.generate_post_time(),
                    user=user
                ))

        return posts



       
    # Todo: def generate create time
    def generate_post_time(self):

        now = datetime.now()
        max_seconds = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        random_seconds = random.uniform(0, max_seconds)
        random_time = now - timedelta(seconds=random_seconds)

        #required format: YYYY-MM-DDTHH:MM:SS.000Z
        return random_time.strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'

    def posts_topic_dist(self, generated_posts_dict, total_posts):
        topic_distribution = {}
        topics = list(generated_posts_dict.keys())  # List of topics available

        percentages = self.random_percentage_distribution(len(topics))# Generate random percentages for each topic that sum to 100

        for i, topic in enumerate(topics):
            topic_distribution[topic] = int(total_posts * percentages[i] / 100)

        return topic_distribution
    
    def random_percentage_distribution(self, n):
        #function creates a random distribution
        percentages = [random.randint(1, 100) for _ in range(n)]
        total = sum(percentages)
        return [int(p * 100 / total) for p in percentages]
    
    def posts_emotions_dist_unif(self, emotions_dict, total_posts_for_topic):
        emotion_distribution = {}
        emotions = list(emotions_dict.keys())
        
        
        posts_per_emotion = total_posts_for_topic // len(emotions)
        remaining_posts = total_posts_for_topic % len(emotions)  # Handle any remainder

        for emotion in emotions:
            emotion_distribution[emotion] = posts_per_emotion

        for _ in range(remaining_posts):
            selected_emotion = random.choice(emotions)
            emotion_distribution[selected_emotion] += 1

        return emotion_distribution