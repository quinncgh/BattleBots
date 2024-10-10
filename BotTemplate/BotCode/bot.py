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
        
        prompt_version = "variant_1"
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
        return new_users

    def generate_content(self, datasets_json, users_list):

        # It needs to return json with the users and their description and the posts to be inserted.
        
        template_version = "variant_2"
        # model = "gpt-3.5-turbo"
        model = "gpt-4o"

        real_user_list = self.get_realuser_list(datasets_json)
        filled_prompt = self.fill_prompt_template_post(real_user_list,template_version)
        # print()
        # print("Complete Prompt for generating posts:")
        # print(filled_prompt)

        generated_posts = self.send_prompt_post(filled_prompt,model)
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
        session_vars = self.get_session_variables(session_info) # get all the session info variables from the session_info object
        filled_prompt = self.fill_prompt_template(prompt_template, session_vars) #prepare the filled propmpt
        return filled_prompt

    def send_prompt_user(self,prompt,llm_model):
    
        try:
            response = openai.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
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
    
    def build_prompts_data(self, real_user_list):
        # This function will create the data part for the prompt and filled into a template later
        # The modification of this function will focus on how to select the user & their post such that the data is representitive
        user_info_str = ""

        if len(real_user_list) >= 5:
            # More than 5 users: Randomly select 5 users and use 1 post from each
            selected_users = random.sample(real_user_list, 5)
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
            # Less than 5 users: Use at least 2 posts from each user until reaching 5 posts
            post_count = 0
            for i, user in enumerate(real_user_list, start=1):
                user_posts = user.posts if user.posts else ["This user does not have any posts"]
                num_posts_to_add = min(2, len(user_posts))  # Use at least 2 posts or as many as available
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

        return user_info_str

    def fill_prompt_template_post(self,real_user_list, prompt_ver):
        # This function will create a complete prompt with user's info and posts
    
        # Get the template for generating content
        all_prompt_template = self.load_prompt_template()
        prompt_template = all_prompt_template["post_generation"].get(prompt_ver)

        user_info_str = self.build_prompts_data(real_user_list)# prepare the data(user info & posts)
        filled_prompt = prompt_template.format(
            topic=self.topic,
            keywords=self.keywords,
            user_info_str=user_info_str
        )
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
                    max_tokens=1000,
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
    
    def generate_new_posts(self,users_list, generated_posts_list):
        posts = []  
        min_posts_per_user = 5
        max_posts_per_user = 6
        total_posts = len(generated_posts_list)
        # print(f"\nNumber of Post Genreated: {total_posts}")

        # To track the index of the posts
        post_index = 0

        for user in users_list:
            user_posts = []
            num_posts_for_user = random.randint(min_posts_per_user, max_posts_per_user)

            for _ in range(num_posts_for_user):#assign posts to users
                if post_index < total_posts:
                    user_posts.append(generated_posts_list[post_index])
                    post_index += 1
                else:
                    # If no generated posts are left, add a message for now, later allow to generate a post
                    # Todo: generate a message
                    user_posts.append("This user has no generated post.")

            # Create NewPost objects for the user and append them to posts
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

