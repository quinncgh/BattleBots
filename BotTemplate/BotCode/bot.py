from abc_classes import ABot
from teams_classes import NewUser, NewPost
from BotTemplate.BotCode.users import RealPost, RealUser
from datetime import datetime,timedelta
from tqdm import tqdm
import openai 
import random
import json
import time
import re

# key1 = 'sk-proj-Ph_DceD2n4-Ql-PU3jINorXb1AL4l_rYLfZ0BYMcGB2gbS3jvxt_oDg72S4ANsMJvJdtg1NOQqT3BlbkFJsI18YT'
# key2 = '_wyezcDS4DK6ZuP2WKSzfDE4LApVlVtc3_BZWR9iuTSCmGDpAnnLjrGVi8tGL5187nAA'

key1 = "sk-svcacct-2rv3A4L9WTdhiSSANdL6hEnPsATrXhYDGaP_"
key2 = "1mtollWg76zPXuk_wFTZ__MJS6VmT3BlbkFJAGyZbOKaiySHpLQY_KpBiz_q29lkDPF6oEmEmah-S2hQPqi2En8PAJW1rp79etcA"
key = key1 + key2

openai.api_key = key

class Bot(ABot):

    #Note that v1 suggests the original version of the functions, create_user and generate_content are the test version for round 5 
    #Ask if we can modify the log such that we cannot record the category information
    def __init__(self):
        # __init__ will store the session info for generating content
        self.topic = None
        self.keywords = None
        self.lang = None
        self.user_labels = {} #use for identifying different type of user in generate content

    def create_user(self, session_info):
        # print(vars(session_info)) # print all the data in the session_info
        # self.data_analyzing_tool("978726274779832320")
        # return None
        model = "gpt-4o"
        template_ver_list = ["test_1","test_2"]
        users_list = []
        group_id = 1

        for template_ver in template_ver_list:          
            sample_usr_info = self.load_sample_user()
            prompt1 = self.generate_prompt_user_vtest(sample_usr_info,template_ver) 
            # print("Prompt for generating Users: ")
            # print(prompt1)
            generated_users_json = self.send_prompt_user(prompt1,model)# return  json data 
            generated_users_list = json.loads(generated_users_json)  # json type to a list
            users_list.extend(generated_users_list)
            group_label = f"generated_user_group_{group_id}"
            self.user_labels.update({user["username"]: group_label for user in generated_users_list if "username" in user})
            group_id += 1
        #     # print("List of new users: ")
        #     # print(generated_users_list)# list of new users, each users is a dictionary
        
        # real user control group 1, real users generated posts
        real_users_1 = self.select_real_user(users_list)
        current_usernames_1 = ",".join([user["username"] for user in real_users_1])
        prompt3 = self.generate_prompt_user_vtest(current_usernames_1,"test_3")
        # print("Prompt for generating new usernames: ")
        # print(prompt3)

        modified_usrname_str_1 = self.send_prompt_user(prompt3,model)
        modified_usrname_list_1 = modified_usrname_str_1.split(",")
        # print("New Usernames for existing user")
        # print(modified_usrname_list_1)

        for i, user in enumerate(real_users_1):
            if i < len(modified_usrname_list_1):
                user["username"] = modified_usrname_list_1[i]
        self.user_labels.update({user["username"]: "real_users_group_1" for user in real_users_1 if "username" in user})
        users_list.extend(real_users_1)

        # real user control group 2, real users real content
        real_users_2 = self.select_real_user(users_list)
        current_usernames_2 = ",".join([user["username"] for user in real_users_2])
        prompt4 = self.generate_prompt_user_vtest(current_usernames_2,"test_3")
        # print("Prompt for generating new usernames: ")
        # print(prompt4)

        modified_usrname_str_2 = self.send_prompt_user(prompt4,model)
        modified_usrname_list_2 = modified_usrname_str_2.split(",")
        # print("New Usernames for existing user")
        # print(modified_usrname_list_1)

        for i, user in enumerate(real_users_2):
            if i < len(modified_usrname_list_2):
                user["username"] = modified_usrname_list_2[i]
        self.user_labels.update({user["username"]: "real_users_group_2" for user in real_users_2 if "username" in user})
        users_list.extend(real_users_2)

        new_users = [
            NewUser(
                username=user["username"],
                name=user["name"],
                description=user.get("description", ""),  
                location=user.get("location", None)          
            )
            for user in users_list
        ]

        # print(self.user_labels)
        return new_users

    def generate_content(self, datasets_json, users_list):

        # print(vars(datasets_json))
        template_version = "test_1"
        model = "gpt-4o"

        # emotion_list = ["joyful","sad","angry","surprised","disgusted","loving","hopeful","pride","neutral"]
        # topic_list = [self.topic,"sports","celebrity news","fashion","music","TV shows","technology","no_topic"]
        emotion_list = ["joyful","sad","angry","surprised","loving","neutral"]
        topic_list = [self.topic,"sports","celebrity news","music","iphone 17 rumors"]

        generated_posts = {}
        
        #temp test : fast content generating
        # placeholder = "The content might contain content that needs to verify your age"
        # generated_posts = {}
        # for topic in topic_list:
        #     generated_posts[topic] = {}
        #     for emotion in emotion_list:
        #         generated_posts[topic][emotion] = [placeholder] * 100
        # print("finish generating all the posts (fast)")

        for topic in tqdm(topic_list, desc="Processing Posts topics"):
            generated_posts[topic] = {}
            for emotion in tqdm(emotion_list, desc=f"Processing emotions for {topic}", leave=False):
                filled_prompt = self.fill_prompt_post_vtest(template_version, topic=topic, emotion=emotion)
                # print()
                # print("Complete Prompt for generating posts:")
                # print(filled_prompt)
                # print()
                # print()

                # if topic != None and topic != "no_topic":print(f"Content for the topic:'{topic}' with emotion:'{emotion}'")
                # else:print(f" Daily Routines Style contents with emotion:'{emotion}'")
                content_one_sentiment = self.send_prompt_post(filled_prompt,model)
                generated_posts[topic][emotion] = content_one_sentiment
        

        new_posts_list = self.assign_posts(users_list,generated_posts,topic_list,emotion_list)
        return new_posts_list


    # def create_user_v1(self, session_info):
    #     # print(vars(session_info)) # print all the data in the session_info
    #     prompt_version = "variant_3"
    #     # model = "gpt-3.5-turbo"
    #     model = "gpt-4o"
    #     user_num = 15

    #     prompt = self.generate_prompt_general(session_info,prompt_version,user_num) # prompt for generating use
    #     # print("Prompt for generating Users: ")
    #     # print(prompt)

    #     generated_users_json = self.send_prompt_user(prompt,model)# return  json data 
    #     generated_users_list = json.loads(generated_users_json)  # json type to a list
    #     # print("List of new users: ")
    #     # print(generated_users_list)# list of new users, each users is a dictionary
        
    #     new_users = [
    #         NewUser(
    #             username=user["username"],
    #             name=user["name"],
    #             description=user.get("description", ""),  
    #             location=user.get("location", None)          
    #         )
    #         for user in generated_users_list
    #     ]
    #     # print(new_users)
    #     return new_users

    # def generate_content_v1(self, datasets_json, users_list):

    #     # It needs to return json with the users and their description and the posts to be inserted.
    #     # print(vars(datasets_json))
        
    #     template_version = "variant_3"
    #     # model = "gpt-3.5-turbo"
    #     model = "gpt-4o"

    #     emotion_list = ["joyful","sad","angry","surprised","neutral"]
    #     topic_list = [self.topic,"sports","no specified"]
    #     # emotion_list = ["joyful","neutral"]
    #     # topic_list = [self.topic]
    #     real_user_list = self.get_realuser_list(datasets_json)
    #     generated_posts = {}
        
    #     for topic in tqdm(topic_list, desc="Processing topics"):
    #     # for topic in topic_list:
    #         generated_posts[topic] = {}
    #         # for emotion in emotion_list:
    #         for emotion in tqdm(emotion_list, desc=f"Processing emotions for {topic}", leave=False):
    #             if topic == "not secificed " or topic == None: filled_prompt = self.fill_prompt_template_post(real_user_list, "variant_4", topic=topic, keywords=self.keywords, emotion_str=emotion)
    #             else:filled_prompt = self.fill_prompt_template_post(real_user_list, template_version, topic=topic, keywords=self.keywords, emotion_str=emotion)
    #             # print()
    #             # print("Complete Prompt for generating posts:")
    #             # print(filled_prompt)
    #             content_one_sentiment = self.send_prompt_post(filled_prompt,model)
    #             # print(content_one_sentiment)
    #             generated_posts[topic][emotion] = content_one_sentiment

    #     new_posts_list = self.generate_new_posts(users_list,generated_posts)
    #     return new_posts_list

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

    def get_session_variables_username(self, session_info, user_num):
        #this get session variable will only get the first 20 users of list of username
        self.topic = session_info.influence_target.get("topic", "no specific topic") if session_info.influence_target else "no specific topic"
        self.keywords = ', '.join(session_info.influence_target.get("keywords", [])) if session_info.influence_target else "no specific"
        self.language = session_info.lang if session_info.lang else "unknown"
        usernames = session_info.metadata.get("usernames", [])[:20] if session_info.metadata else []
    
        return {
            "user_num": user_num,
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
    
    def generate_prompt_general(self,session_info,prompt_ver, user_num):
        all_templates = self.load_prompt_template() #load all the templates from the json file
        prompt_template = all_templates["user_generation"].get(prompt_ver)

        # session_vars = self.get_session_variables(session_info) # get all the session info variables from the session_info object
        session_vars = self.get_session_variables_username(session_info, user_num) #only get the usernames as sample for gpt

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
            # print("Response from LLM for create users:")
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
       
    def send_prompt_post(self, filled_prompt, model, max_retries=10):
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
                # print()
              
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
                print(f"Error calling LLM API: {e}. Retrying Sending Propmt to OpenAi in 15 seconds")
                time.sleep(15) 

        # If max retries reached, return a fallback message
        print("Max retries reached. Returning fallback message.")
        return ["The users posts might contain restricted content, please confirm your age"] * 20  
    


        return posts

    def generate_new_posts(self, users_list, generated_posts_dict, min_posts_per_user=20, max_posts_per_user=30):
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
            # print(len(user_posts))
                
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
        start_time = now - timedelta(days=365)
        random_seconds = random.uniform(0, (now - start_time).total_seconds())
        random_time = start_time + timedelta(seconds=random_seconds)

        # Required format: YYYY-MM-DDTHH:MM:SS.000Z
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
    
    # Functions For Comparison Test Versions:
    def load_sample_user(self):
        try:

            with open('BotTemplate/BotCode/realdata.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            if "users" not in data:
                raise KeyError("The JSON file does not contain the 'users' field.")
            
            users = data["users"]
            selected_users = random.sample(users, min(3, len(users)))
            
            user_info_str = ""
            for user in selected_users:
                username = user.get("username", "N/A")
                name = user.get("name", "N/A")
                description = user.get("description", "N/A")
                location = user.get("location", "N/A")
                
                user_info_str += (
                    f"username: {username}\n"
                    f"name: {name}\n"
                    f"description: {description}\n"
                    f"location: {location}\n\n"
                )
            
            return user_info_str.strip()
        
        except KeyError as e:
            return f"Error: Missing key in JSON data - {e}"
        except json.JSONDecodeError:
            return "Error: Failed to parse JSON data."
        except Exception as e:
            return f"Error: {str(e)}"
        
    def generate_prompt_user_vtest(self,sample_usr_info,template_ver):

        all_templates = self.load_prompt_template() #load all the templates from the json file
        prompt_template = all_templates["user_generation"].get(template_ver)
        if template_ver == "test_3":
            filled_prompt = prompt_template.format(
                user_names = sample_usr_info
            )
        else:
            filled_prompt = prompt_template.format(
                sample_user_info = sample_usr_info
            )
        return filled_prompt
    
    def select_real_user(self,user_exists):
        try:
            with open('BotTemplate/BotCode/realdata.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            if "users" not in data:
                raise KeyError("The JSON file does not contain the 'users' field.")
            
            users = data["users"]
            filtered_users = [user for user in users if user.get("username") not in user_exists]
            if not filtered_users:
                raise ValueError("No eligible users available after filtering.")

            selected_users = random.sample(filtered_users, min(3, len(filtered_users)))
        
            user_info_list = []
            for user in selected_users:
                original_username = user.get("username", "N/A")

                modified_username = (f"{original_username}1" if original_username in user_exists else original_username)
                user_info = {
                    "username": modified_username,
                    "name": user.get("name", "N/A"),
                    "description": user.get("description", "N/A"),
                    "location": user.get("location", "N/A")
                }
                user_info_list.append(user_info)
        
            
            return user_info_list
    
        except KeyError as e:
            return f"Error: Missing key in JSON data - {e}"
        except json.JSONDecodeError:
            return "Error: Failed to parse JSON data."
        except Exception as e:
            return f"Error: {str(e)}"
        
    def fill_prompt_post_vtest(self,template_ver, topic, emotion):

        all_prompt_template = self.load_prompt_template()
        if topic != None and topic != "no_topic":
            prompt_template = all_prompt_template["post_generation"].get(template_ver)
            filled_prompt = prompt_template.format(
                topic=topic,
                emotion = emotion
            )
        else:
            prompt_template = all_prompt_template["post_generation"].get("no_topic")
            filled_prompt = prompt_template.format(
                emotion = emotion
            )
        return filled_prompt
    
    def load_real_posts(self):
        try:
            with open('BotTemplate/BotCode/realdata.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
            if "posts" not in data:
                raise KeyError("The JSON file does not contain the 'posts' field.")
            post_list = [post["text"] for post in data["posts"] if "text" in post]
            return post_list

        except FileNotFoundError:
            print("Error: JSON file not found.")
            return []
        except KeyError as e:
            print(f"Error: Missing key in JSON data - {e}")
            return []
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON data.")
            return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
        
    def assign_posts(self,users_list,generated_posts,topic_list,emotion_list):
        print(users_list[1])
        posts = []
        real_posts = self.load_real_posts()

        for user in users_list:
            user_posts = []
            user_categ = self.user_labels[user.username]

            if user_categ == "real_users_group_1":
                selected_posts = random.sample(real_posts, 15)#30
                user_posts.extend(selected_posts)
                for post in selected_posts:real_posts.remove(post)
            elif user_categ == "generated_user_group_1":
                selected_posts = random.sample(real_posts, 20)#35
                user_posts.extend(selected_posts)
                for post in selected_posts:real_posts.remove(post)
            else: 
                if user_categ == "real_users_group_2": total_num_post = 15 #36
                else:total_num_post = 20
                topic_dist = self.topic_distribution(topic_list, total_num_post)
                for topic, topic_post_count in topic_dist.items():
                    emotion_dist = self.emotion_distribution(emotion_list, topic_post_count)
                    for emotion, emotion_post_count in emotion_dist.items():
                        available_posts = generated_posts.get(topic, {}).get(emotion, [])
                        selected_posts = random.sample(available_posts, min(emotion_post_count, len(available_posts)))
                        user_posts.extend(selected_posts)
                        for post in selected_posts:
                            generated_posts[topic][emotion].remove(post)
            # print(user_posts)
            for post_text in user_posts:
                posts.append(NewPost(
                    text=post_text,
                    author_id=user.user_id,
                    created_at=self.generate_post_time(),
                    user=user
                ))
    
        
        return posts

    def emotion_distribution(self, emotion_list, topic_post_num):
        # number of each emotion follows a uniform distribution
        num_emotions = len(emotion_list)
        posts_per_emotion = topic_post_num // num_emotions
        remaining_posts = topic_post_num % num_emotions

        post_distribution = {emotion: posts_per_emotion for emotion in emotion_list}
        
        for _ in range(remaining_posts):
            selected_emotion = random.choice(emotion_list)
            post_distribution[selected_emotion] += 1
        
        return post_distribution
    
    def topic_distribution(self, topic_list, total_num_post):


        selected_topics = random.sample(topic_list, 4)
        ratios = [0.4, 0.3, 0.2, 0.1]
        post_distribution = {}
        remaining_posts = total_num_post

        for i, topic in enumerate(selected_topics):
            if i == len(selected_topics) - 1:
                num_posts = remaining_posts
            else:
                num_posts = int(total_num_post * ratios[i])
                remaining_posts -= num_posts
            post_distribution[topic] = num_posts
        return post_distribution

    def data_analyzing_tool(self, user_id):
        try:
            with open('BotTemplate/BotCode/realdata5.json', 'r', encoding='utf-8') as file:
                data = json.load(file)

            if "posts" not in data:
                raise KeyError("The JSON file does not contain the 'posts' field.")

            print(f"Posts by User ID: {user_id}")
            found_posts = False
            for post in data["posts"]:
                if post.get("author_id") == user_id:
                    # print(post.get("text", "No text available"))
                    print(post.get("created_at"))
                    print()
                    found_posts = True

            if not found_posts:
                print(f"No posts found for User ID: {user_id}")

        except FileNotFoundError:
            print("Error: JSON file not found.")
        except KeyError as e:
            print(f"Error: Missing key in JSON data - {e}")
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON data.")
        except Exception as e:
            print(f"Error: {str(e)}")