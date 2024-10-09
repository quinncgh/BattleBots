# Test code:
from api_requests import SessionInfo,SubSessionDataset
from BotTemplate.BotCode.bot import Bot
from teams_classes import User, NewUser, NewPost


def generate_user_test_1():

    session_data = {
    "session_id": 0,
    "lang": "en",
    "metadata": {
        "topics": ["nba laker new season"],
        "user_distribution_across_time": ["morning", "afternoon"],
        "users_average_amount_posts": 5,
        "users_average_amount_words_in_post": 50,
        "users_average_z_score": 1.5
    },
    "influence_target": {
        "topic": "NBA",
        "keywords": ["laker", "james"]
    },
    "start_time": "2023-01-01T00:00:00Z",
    "end_time": "2023-01-01T01:00:00Z",
    "sub_sessions_info": [
        {
        "sub_session_id": 1,
        "start_time": "2023-01-01T00:30:00Z",
        "end_time": "2023-01-01T01:00:00Z"
        }
    ],
    "users": [
        {"username": "james123"},
        {"username": "sports_kong"},
        {"username": "luke_the_k"}
    ]
    }
    session_info = SessionInfo(session_data)

    # Instantiate the bot and create users
    bot = Bot()
    generated_users = bot.create_user(session_info)
    # print(generated_users)

def generate_post_test1():
   subsession_data = {
   "session_id":-1,
   "sub_session_id":4,
   "posts":[
      {
         "text":"oh wow https://t.co/twitter_link",
         "created_at":"2024-03-27T00:06:30.000Z",
         "id":"1772777177479541156",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"mitchy 🥲 https://t.co/twitter_link",
         "created_at":"2024-03-27T15:46:45.000Z",
         "id":"1773013799542391180",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"I LUV IT SO GOOD BYEEEEEEE https://t.co/twitter_link",
         "created_at":"2024-03-27T16:05:30.000Z",
         "id":"1773018517123563925",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"does anyone have the guts tour merch prices in CAD",
         "created_at":"2024-03-27T16:25:29.000Z",
         "id":"1773023546840617258",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"the amount of likes is also concerning https://t.co/twitter_link",
         "created_at":"2024-03-27T18:55:40.000Z",
         "id":"1773061341621768259",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"just realized olivia’s music is gonna change forever for me bc songs are never the same after a concert",
         "created_at":"2024-03-28T01:41:00.000Z",
         "id":"1773163348919562318",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"goodnight  https://t.co/twitter_link",
         "created_at":"2024-03-28T05:12:43.000Z",
         "id":"1773216627888197634",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"a sweet lady at timmies bought me and my friend coffee today 😭❤️❤️❤️❤️❤️❤️ made my day",
         "created_at":"2024-03-28T14:54:33.000Z",
         "id":"1773363051212755114",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"YES YES YES YES https://t.co/twitter_link",
         "created_at":"2024-03-28T18:41:48.000Z",
         "id":"1773420240019370146",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"just calculus things https://t.co/twitter_link",
         "created_at":"2024-03-28T18:49:41.000Z",
         "id":"1773422223455326316",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"three empty words, patience, hold on https://t.co/twitter_link",
         "created_at":"2024-03-28T19:21:05.000Z",
         "id":"1773430126211973555",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"Goalies tonight are Varlamov for Stolarz. #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T22:38:49.000Z",
         "id":"1773479888424501261",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"Under way  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:11:23.000Z",
         "id":"1773488082823622893",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"Varlamov with a big save on Barkov after the #Isles struggle to clear the puck.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:14:13.000Z",
         "id":"1773488797952458985",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"Simon Holmstrom a scratch tonight for the #Isles.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:14:45.000Z",
         "id":"1773488929028575451",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"The good news: the #Isles did a good job of keeping the Panthers on the perimeter. The bad news: they can’t clear their own zone  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:17:45.000Z",
         "id":"1773489686683537779",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"Varlamov stops Kulikov as the #Isles continue to be stuck in their own zone  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:18:40.000Z",
         "id":"1773489917357703590",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"#Isles get first SOG 6 1/2 minutes into the game  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:21:23.000Z",
         "id":"1773490599804445116",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"#Isles lead 1-0 Pulock scores through a screen. MacLean was in the crease and was battling with Kulikov. Panthers will review it.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:23:21.000Z",
         "id":"1773491094329626991",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"No goal after review.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:24:15.000Z",
         "id":"1773491319572164670",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"And less than one minute later Tarasenko scores with by bouncing it in off Pageau’s stick.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:25:55.000Z",
         "id":"1773491740621631849",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"nah dude i’m still mad about being called obsessive and a person who only watches hockey cuz the men r hot just because i made of list of my top NHL players i am very upset",
         "created_at":"2024-03-28T23:26:06.000Z",
         "id":"1773491786821878185",
         "author_id":"976978627425312768",
         "lang":"en"
      },
      {
         "text":"Pulock scores and this one counts. Banked it in off the far post. 1-1 game now.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:34:30.000Z",
         "id":"1773493900746920297",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"Panthers with a flurry of shots with a lot of bodies in front but Varly kept it out.  #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:35:30.000Z",
         "id":"1773494150429589830",
         "author_id":"787467017406251008",
         "lang":"en"
      },
      {
         "text":"Tied 1-1 after one period. #Isles thoroughly outplayed for most of the period and fortunate to be even. SOG 9-6 Florida. #Isles #NHL #NYIvsFLA",
         "created_at":"2024-03-28T23:46:57.000Z",
         "id":"1773497035481551051",
         "author_id":"787467017406251008",
         "lang":"en"
      }
   ],
   "users":[
      {
         "id":"976978627425312768",
         "username":"marnerhugs",
         "name":"j-lynn",
         "description":"MM16 enthusiast — they/she ❣️",
         "location":"None",
         "tweet_count":12,
         "z_score":-0.8284953579
      },
      {
         "id":"787467017406251008",
         "username":"IceWarsNYRvsNYI",
         "name":"Gil Martin",
         "description":"Hockey historian and author of Ice Wars the book that tells the story behind the Rangers-Islanders rivalry and host of the Locked On Islanders Podcast.",
         "location":"New York, USA",
         "tweet_count":13,
         "z_score":-0.7890129548
      }
   ]
}
   
   bot = Bot()
   subsession_info = SubSessionDataset(subsession_data)
   real_user_list = bot.get_realuser_list(subsession_info)
   filled_prompt = bot.fill_prompt_template_post(real_user_list)
   posts = bot.send_prompt_post(filled_prompt,users_list=None)



if __name__ == "__main__":
    generate_post_test1()
