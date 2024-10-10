# This file stores the old versions of bot

from abc_classes import ABot
from teams_classes import NewUser, NewPost
from BotTemplate.BotCode.users import RealPost, RealUser
import openai 
import random
import json
import re


class Bot(ABot):

    def __init__(self):
        # __init__ will store the session info for generating content
        self.topic = None
        self.keywords = None
        self.lang = None

    def create_user(self, session_info):

        # Example:
        # new_users = [
        #     NewUser(username="TestBot", name="Emilie", description="I'm a test bot."),
        # ]

        
        #part 1: process the session_info (optional for now, depends on the implimentation)
        #part 2: use the processed session_info to build the prompt
        #part 3: receive the answer (ideally in json data format) and processed the data 
        #part 4: use the processed received data to build users 
        prompt = self.generate_prompt_general(session_info,"variant_1")
        # print(prompt)
        generated_users_json = self.send_prompt_api(prompt)# return  json data 
        generated_users_list = json.loads(generated_users_json)  # json type to a list
        print(generated_users_list)
        new_users = [
            NewUser(
                username=user["username"],
                name=user["name"],
                description=user.get("description", None),  
                location=user.get("location", None)          
            )
            for user in generated_users_list
        ]
        return new_users

    def generate_content(self, datasets_json, users_list):

        # It needs to return json with the users and their description and the posts to be inserted.
        # Test:
        # print(vars(datasets_json))
        # posts = self.process_test(datasets_json,users_list)
        # return posts

        real_user_list = self.get_realuser_list(datasets_json)
        filled_prompt = self.fill_prompt_template_post(real_user_list)
        posts = self.send_prompt_post(filled_prompt,users_list)
        return posts

        # Example 
        # posts = []
        # for j in range(len(users_list)):
        #     posts.append(NewPost(text="Pandas are amazing!", author_id=users_list[j].user_id, created_at='2024-08-18T00:20:30.000Z',user=users_list[j]))
        # return posts
    
        #part 1:process subsession_info(will need a more sophsiticated and efficient method to extract the posts) 
        #part 2:use the processed sub-session data to build prompts
        #part 3:receive the answer (ideally in json data format) and processed the data
        #part 4:use the received data to build prompts


    #functions for both create user and genereate_user
    def load_prompt_template(self,usage,prompt_ver):
        try:
            with open('BotTemplate/BotCode/prompts.json', 'r', encoding='utf-8') as file:
                prompts_template = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found.")
            return None
        
        prompt_template = prompts_template[usage].get(prompt_ver) 
        return prompt_template
            
    #functions for create_user
    def get_session_variables(self, session_info):
        # print(vars(session_info))
        self.topic = session_info.influence_target.get("topic", "no specific topic") if session_info.influence_target else "no specific topic"
        self.keywords = ', '.join(session_info.influence_target.get("keywords", [])) if session_info.influence_target else "no specific"
        self.language = session_info.lang if session_info.lang else "unknown"

        return {
            # "topic": session_info.influence_target.get("topic", "") if session_info.influence_target else "no specific topic",
            # "keywords": ', '.join(session_info.influence_target.get("keywords", [])) if session_info.influence_target else "no specific",
            # "language": session_info.lang if session_info.lang else "unknown",

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
    
    def generate_prompt_1(self,session_info):

        topic = session_info.influence_target["topic"]
        keywords = ', '.join(session_info.influence_target["keywords"])
        language = session_info.lang
        real_users = ', '.join([user["username"] for user in session_info.users])

        prompt = f"""
        Based on the following session data, generate 3 user profiles. Each profile should include a username, name, and optional fields: a description (with a 50% chance of inclusion) and location (with a 50% chance of inclusion). The profiles should reflect the given topic and keywords, and should be formatted in JSON.

        Session Data:
        - Topic: {topic}
        - Keywords: {keywords}
        - Language: {language}

        Example Real Users:
        {real_users}

        Output 3 fictional user profiles in JSON format as follows:
        [
            {{
                "username": "<string>",
                "name": "<string>",
                "description": "<string or null if not included>",
                "location": "<string or null if not included>"
            }},
            ...
        ]
        """
        return prompt

    def generate_prompt_general(self,session_info,prompt_ver):
        try:
            with open('BotTemplate/BotCode/prompts.json', 'r', encoding='utf-8') as file:
                prompts_template = json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found.")
            return None 
        
        prompt_template = prompts_template["user_generation"].get(prompt_ver)          
        session_vars = self.get_session_variables(session_info)
        filled_prompt = self.fill_prompt_template(prompt_template, session_vars)
        return filled_prompt

    def send_prompt_api(self,prompt):
    
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.7
            )
            # print(response)
            generated_users = response.choices[0].message.content# Parse the response and convert it to JSON
            # print(generated_users)
            return generated_users 
        
        except Exception as e:
            print(f"Error Calling Large Model : {e}")
            return None

    #functions for generate_content
    def process_test(self,datasets_json, users_list):
        test_prompt = """
        Please generate 3 social media posts based on the following examples:
        'I cannot wait to see LeBron James and his son play together this season!!!',
        'Not sure about Lakers this year, still think Clippers will win the finals this season',
        'If Curry will transfer to Lakers this year, LeBron probably could have another ring.'

        Note that you do not need to strictly match the samples. 
        Do not include any numbering or markers. Just return the posts as plain text, separated by new lines, and return the posts as strings in a Python list.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.7
            )
            generated_posts = response.choices[0].message.content
            # print(generated_users)

        except Exception as e:
            print(f"Error Calling Large Model : {e}")

        # print(generated_posts)
        generated_posts_list = generated_posts.split('\n')
        generated_posts_list = [post.strip() for post in generated_posts_list if post.strip()]
        print(generated_posts_list)

        posts = []
        # Iterate over both users_list and generated_posts_list in parallel
        for j in range(len(users_list)):
            if j < len(generated_posts_list):  # Ensure there are enough generated posts
                # Use the generated post content for the text field
                post_text = generated_posts_list[j]
            else:
                # In case there are fewer posts than users, fallback to a default message
                post_text = "This user has no generated post."

            # Create a NewPost object using the generated post text and assign to the corresponding user
            posts.append(NewPost(
                text=post_text,
                author_id=users_list[j].user_id,
                created_at='2024-08-18T00:20:30.000Z',
                user=users_list[j]
            ))
        print("check point 1")
        
        return posts
    
    def get_realuser_list(self,datasets_json):
        user_dict = {}

        for user_data in datasets_json.users:
            user = RealUser()  # Create an empty RealUser object
            user.id = user_data['id']
            user.tweet_count = user_data['tweet_count']
            user.z_score = user_data['z_score']
            user.username = user_data['username']
            user.name = user_data['name']
            user.description = user_data.get('description')  # Use .get() in case 'description' is missing
            user.location = user_data.get('location')  # Use .get() to safely handle None
            
            # Add the user to the dictionary by their ID
            user_dict[user.id] = user
        
        for post_data in datasets_json.posts:
            post = RealPost()  # Create an empty RealPost object
            post.id = post_data['id']
            post.text = post_data['text']
            post.author_id = post_data['author_id']
            post.created_at = post_data['created_at']
            post.lang = post_data['lang']

        
            if post.author_id in user_dict:
                user_dict[post.author_id].add_post(post)
        
        return list(user_dict.values())
    
    def build_prompts_data(self, real_user_list):
        #The Key point for this function is how to select the posts that representitive
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

    def fill_prompt_template_post(self,real_user_list):

        prompt_template = self.load_prompt_template("post_generation", "variant_2")
        user_info_str = self.build_prompts_data(real_user_list)
        filled_prompt = prompt_template.format(
            topic=self.topic,
            keywords=self.keywords,
            user_info_str=user_info_str
        )
        return filled_prompt
       
    def send_prompt_post(self,filled_prompt,users_list):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": filled_prompt}
                ],
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.7
            )
            generated_posts = response.choices[0].message.content
            # print(generated_users)

        except Exception as e:
            print(f"Error Calling Large Model : {e}")


        generated_posts_dict  = json.loads(generated_posts)
        generated_posts_list = [generated_posts_dict[key] for key in sorted(generated_posts_dict.keys()) if 'post' in key]
        print(generated_posts_list)

        posts = []
        # Iterate over both users_list and generated_posts_list in parallel
        post_id = 10000
        for j in range(len(users_list)):
            post_id += 1
            if j < len(generated_posts_list):  # Ensure there are enough generated posts
                # Use the generated post content for the text field
                post_text = generated_posts_list[j]
            else:
                # In case there are fewer posts than users, fallback to a default message
                # This part could ask LLM or a small model to generate radom messages
                post_text = "This user has no generated post."

            # Create a NewPost object using the generated post text and assign to the corresponding user
            posts.append(NewPost(
                text=post_text,
                author_id=users_list[j].user_id,
                created_at='2024-08-18T00:20:30.000Z',
                user=users_list[j]
            ))

        return posts      
