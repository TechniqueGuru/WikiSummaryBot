import praw
import wikipedia
import time

# Made by /u/DiamondxCrafting.

# Fill in the following information.
username = ""
dev = ""
try:
    reddit = praw.Reddit(client_id="", client_secret="",
                         username=username, password="",
                         user_agent="")
except Exception as e:
    print("#Login failed.", e)


def file_exist_check():  # Check if comment id file exists, if not, create it.
    try:
        open("comment_id.txt", "r")
    except FileNotFoundError:
        open("comment_id.txt", "w")


def comment_id_check(comment_id):  # Check if the comment has already been replied to.
    file_exist_check()
    comment_id_list = open("comment_id.txt", "r+").read().split("\n")
    for comment_id_saved in comment_id_list:
        if comment_id == comment_id_saved:
            return True
            break


def save_comment_id(comment_id):  # Adds comment id to replied to comments list.
    file_exist_check()
    open("comment_id.txt", "a+").write(f"{comment_id}\n")


def extract_phrase(comment_body):  # Extracts search term inbetween "[[" "]]" from comment.
    try:
        if comment_body.find("[[") == -1 or comment_body.find("]]") == -1:  # Return False if usage is incorrect.
            return False
        else:
            return comment_body[comment_body.find("[[") + 2:comment_body.find("]]")]
    except Exception as e:
        print(f"Couldn't extract phrase; {e}.")
        return None


def wiki_link(phrase):  # Returns wikipedia page link.
    if summary != "NotFound" and title != "NotFound":
        try:
            return wikipedia.page(phrase).url
        except wikipedia.exceptions.DisambiguationError as l:
            print(f"Couldn't get wikipedia link; {l}.")
            for search_term in wikipedia.search(phrase):
                try:
                    return wikipedia.page(search_term).url
                    break
                except:
                    pass
            if link == None:
                return "NotFound"
        except wikipedia.exceptions.PageError as l:
            print(f"Couldn't get wikipedia link; {l}.")
            return "NotFound"
    else:
        return "NotFound"


def wiki_title(phrase):  # Returns wikipedia page title.
    if summary != "NotFound":
        try:
            return wikipedia.page(phrase).title
        except wikipedia.exceptions.DisambiguationError as t:
            print(f"Couldn't get wikipedia title; {t}.")
            for search_term in wikipedia.search(phrase):
                try:
                    return wikipedia.page(search_term).title
                    break
                except:
                    pass
            if title == None:
                return "NotFound"
        except wikipedia.exceptions.PageError as t:
            print(f"Couldn't get wikipedia title; {t}.")
            return "NotFound"
    else:
        return "NotFound"


def wiki_summary(phrase):  # Returns wikipedia page summary.
    try:
        return wikipedia.summary(phrase)
    except wikipedia.exceptions.DisambiguationError as s:
        print(f"Couldn't get wikipedia summary; {s}.")
        for search_term in wikipedia.search(phrase):
            try:
                return wikipedia.summary(search_term)
                break
            except:
                pass
        if summary == None:
            return "NotFound"
    except wikipedia.exceptions.PageError as s:
        print(f"Couldn't get wikipedia summary; {s}.")
        return "NotFound"

sub = reddit.subreddit("test")  # Subreddit to get comments from.
user = reddit.redditor(username)

while True:
    if "last_id" in globals():
        sub_comments = sub.comments(params={"before": last_id})
    else:
        sub_comments = sub.comments()

    for comment in sub_comments:
        last_id = comment.name
        print(comment.body)
        if "!wikibot" in comment.body.lower():
            if comment_id_check(comment.id) or comment.author == username:  # Skip comment if already replied to.
                continue

            phrase = summary = title = link = None
            phrase = extract_phrase(comment.body)

            if phrase != False:
                summary = wiki_summary(phrase)
                title = wiki_title(phrase)
                link = wiki_link(phrase)

            if phrase == None or summary == None or title == None or link == None:  # Reply informing the user something went wrong, and to contact the developer.
                try:
                    comment.reply(f"An error has occurred, please contact the [developer](https://www.reddit.com/message/compose/?to={dev}&subject=wikibot_error).\n***\n^[[PM](https://www.reddit.com/message/compose/?to={dev}&subject=Wikibot%20Inquiry) ^| ^Downvote ^to ^delete]")
                    save_comment_id(comment.id)
                except Exception as e:
                    print(f"#Error, "+str(e))
                time.sleep(10 * 60)
            elif phrase == False:  # Informing user of correct usage.
                try:
                    comment.reply(f"Correct usage is '!wikibot [[text here]]'.\n***\n^[[PM](https://www.reddit.com/message/compose/?to={dev}&subject=Wikibot%20Inquiry) ^| ^Downvote ^to ^delete]")
                    save_comment_id(comment.id)
                except Exception as e:
                    print(f"#Error, "+str(e))
                time.sleep(10 * 60)
            elif summary == "NotFound" or title == "NotFound" or link == "NotFound":
                try:
                    comment.reply(f"'{phrase}' does not match any pages. Try another query!\n***\n^[[PM](https://www.reddit.com/message/compose/?to={dev}&subject=Wikibot%20Inquiry) ^| ^Downvote ^to ^delete]")
                    save_comment_id(comment.id)
                except Exception as e:
                    print(f"#Error, "+str(e))
                time.sleep(10 * 60)
            else:
                try:
                    comment.reply(f"#{title}\n\n{summary}\n\n[Wikipedia link]({link}).\n***\n^[[PM](https://www.reddit.com/message/compose/?to={dev}&subject=Wikibot%20Inquiry) ^| ^Downvote ^to ^delete]")
                    save_comment_id(comment.id)
                except Exception as e:
                    print(f"#Error, "+str(e))
                time.sleep(10 * 60)

    my_comments = user.comments.controversial('all')
    for comment in my_comments:  # Goes through each bot's comment and deletes comments with karma < 0.
        if comment.score < 0:
            comment.delete()
