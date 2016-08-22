import re, praw, os, json, sys, time, validators
from random import choice

authorName = "thelinkfixerbot"
USERAGENT = 'A user who helps people fix their links. Created by /u/lucadem1313.'

r = praw.Reddit(USERAGENT)

# post with original comments the bot replied to. Mainly used to make sure that errors people report are real,
# and not just that the commentor fixed the link
postThread = r.get_submission(submission_id='4vo43z')

r.login(authorName, '***')


# list to hold comments that are waiting replies
commentQueue = []

# list of items to remove from commentQueue
commentsToDelete = []

thanks = ["No problem", "My pleasure", "You're welcome", "No trouble", "Anytime"]
emojis = [":P", ":)", "8-)", ":^)", ":3", ":D", ";)", ";/", ":\\", ":|", "xD"]

if not os.path.isfile("linkfixer.json"):
    repliedIds = []
    repliedPosts = []

else:
    with open("linkfixer.json", "r") as f:
        try:
            raw = json.loads(f.read())
            repliedIds = []
            repliedPosts = raw["posts"]
            for post in repliedPosts:
                repliedIds.append(post["id"])
        except ValueError:
            repliedIds = []
            repliedPosts = []

def check_condition(comment):
    commentText = comment.body

    condition = False
    if ")[" in commentText or "](" in commentText:
        if c.author.name != authorName and comment.id not in repliedIds:
            condition = True

    return condition

def bot_action(c, respond):
    messages = r.get_unread()
    for message in messages:
      messageText = message.body.lower()
      replyText = ""
      if "thank" in messageText and "delete comment: " not in messageText:
        replyText = choice(thanks) + " " + choice(emojis)
        
      if "delete comment: " in messageText:
        commentLink = messageText.replace("delete comment: ", "")
        if commentLink != None:
          commentInfo = r.get_submission(commentLink).comments[0]
          parent = r.get_info(thing_id=commentInfo.parent_id)
          
          if commentInfo != None and parent != None and message != None:
            if parent.author != None and message.author != None:
              if parent.author.name == message.author.name or parent.author.name is '[Deleted]':
                commentInfo.edit('This used to be a comment from a bot correcting a user\'s markdown, but the user fixed it.\n\n***\n^(I am a bot, and this action was performed automatically.) [^Feedback](https://np.reddit.com/message/compose?to=lucadem1313&subject=Link%20Fixer%20Bot "Contact to report issues, ask questions, or leave some feedback")')
                replyText = "Bot message deleted. Thank you " + choice(emojis)
              else:
                replyText = "Error deleting comment. You may not be the author of the original comment. If you are, please try again."
            else:
              replyText = "Error fetching comment. Please make sure you do not add anything after the comment url, and try again."
          else:
            replyText = "Error fetching comment. Please make sure you do not add anything after the comment url, and try again."
        else:
          replyText = "Link not found. Please try again and do not modify the message that the bot generates."
        
      try:
        message.reply(replyText)
        message.mark_as_read()
      except praw.errors.RateLimitExceeded as error:
        print 'Rate limit error in message reply'
        break
      except praw.errors.Forbidden as error:
        print 'Forbidden error with message reply. Skipping.'
        break
      except:
        print 'Unknown error with message reply. Skipping.'
        break
    
    text = c.body

    linkList1 = [item for item in text.split("[")]
    linkList2 = [item for item in text.split("(")]
    fixedUrls = []
    someBrokenLinks = False

    for link in linkList1:
        if "](" in link:
            url = link.split("](")[1].split(")")[0].replace(" ", "")
            rawUrl = link.split("](")[1].split(")")[0]
            text = link.split("](")[0]
            rawText = text

            if validators.url(text.lower()) or validators.url("http://"+text.lower()):
                textValidUrl = True
            else:
                textValidUrl = False

            if url != None and text != None and len(url) > 0 and len(text) > 0:
                if textValidUrl and not validators.url(rawUrl.lower()) and not validators.url("http://" + rawUrl.lower()) and url[0] != "#" and url[0] != "/":
                    url = text.replace(" ", "")
                    text = rawUrl

                if "http://" not in url and "https://" and not validators.url(url.lower()) and validators.url("http://"+url.lower()) and len(url) > 0 and len(text) > 0:
                    someBrokenLinks = True
                    url = "http://" + url
                    fixedUrls.append({"url":url, "mdLink":"["+text+"]("+url+")", "original":"["+rawText+"]("+rawUrl+")", "fixed":"\["+text+"\]\("+url+")"})


    for link in linkList2:
        if ")[" in link:
            url = link.split(")[")[1].split("]")[0].replace(" ", "")
            rawUrl = link.split(")[")[1].split("]")[0]
            text = link.split(")[")[0]
            rawText = text

            if validators.url(text.lower()) or validators.url("http://"+text.lower()):
                textValidUrl = True
            else:
                textValidUrl = False

            if url != None and text != None and len(url) > 0 and len(text) > 0:
                if textValidUrl and not validators.url(rawUrl.lower()) and not validators.url("http://" + rawUrl.lower()) and url[0] != "#" and url[0] != "/":
                    url = text.replace(" ", "")
                    text = rawUrl

                if "http://" not in url and "https://" and not validators.url(url.lower()) and validators.url("http://"+url.lower()) and len(url) > 0 and len(text) > 0:
                    someBrokenLinks = True
                    url = "http://" + url
                    fixedUrls.append({"url": url, "mdLink":"["+text+"]("+url+")", "original":"("+rawText+")["+rawUrl+"]", "fixed":"\["+text+"\]\("+url+")"})




    if someBrokenLinks:
        message = '\n\n***\n^(I am a bot, and this action was performed automatically.)\n\n[^Feedback](https://np.reddit.com/message/compose?to=lucadem1313&subject=Link%20Fixer%20Bot "Contact to report issues, ask questions, or leave some feedback") ^| [^Formatting ^Help](https://np.reddit.com/wiki/commenting "Reddit.com markdown guide") ^| [^Subreddit](http://np.reddit.com/r/thelinkfixerbot "Subreddit for bot info") ^| [^Bot ^Code](https://github.com/lucadem1313/thelinkfixerbot "Code on GitHub")' # ^| [^Original ^Comment]('+pasteUrl+' "PasteBin of orinal comment")'

        commentText = "Uh-oh **"+c.author.name+"**, it looks like there's **"+str(len(fixedUrls))+"** broken markdown links in your post. I've listed them below:\n\nFixed Link | Original Markdown | Fixed Markdown\n:---------:|:----------:|:----------:"
        for link in fixedUrls:
            commentText += "\n" + link["mdLink"] + " | " + link["original"] + " | " + link["fixed"]
        commentText += message
        print c.id + "\n"
        if respond:
            while True:
                try:
                    reply = postThread.add_comment('[Original Comment]('+c.permalink.replace("//www.", "//np.")+') by '+c.author.name+'\n\n***\n\n>' + c.body.replace("\n", "\n>") + "\n\n***")
                    newComment = c.reply(commentText + ' ^| [^Original ^Comment]('+reply.permalink.replace("//www.", "//np.")+' "Record of original comment")')
                    newComment.edit(newComment.body + ' ^| [^Delete ^Comment](https://np.reddit.com/message/compose?to=thelinkfixerbot&subject=Delete%20Comment&message=delete%20comment:%20'+newComment.permalink+' "Just Click Send")')
                    repliedPosts.append({"id":c.id, "reply":reply.id, "fixedLinks":len(fixedUrls)})
                    with open("linkfixer.json", "w") as f:
                        f.write(json.dumps({"posts":repliedPosts}))

                    break
                except praw.errors.RateLimitExceeded as error:
                    print '\tSleeping for %d seconds' % error.sleep_time
                    time.sleep(error.sleep_time)
                except praw.errors.Forbidden as error:
                    print 'Forbidden error. Skipping.'
                    break
                except:
                    print 'Unknown error. Skipping.'
                    break



for c in praw.helpers.comment_stream(r, 'all'):
	if check_condition(c):
		bot_action(c, respond=True)
