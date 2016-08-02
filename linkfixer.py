import re, praw, os, json, sys, time, validators
from random import choice

authorName = "thelinkfixerbot"
USERAGENT = 'A user who helps people fix their links. Created by /u/lucadem1313.'

r = praw.Reddit(USERAGENT)
postThread = r.get_submission(submission_id='4vo43z')


r.login(authorName, '***')



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
    text = c.body

    linkList1 = [item for item in text.split("[")]
    linkList2 = [item for item in text.split("(")]
    fixedUrls = []
    someBrokenLinks = False

    for link in linkList1:
        if "](" in link:
            url = link.split("](")[1].split(")")[0].replace(" ", "").lower()
            rawUrl = link.split("](")[1].split(")")[0]
            text = link.split("](")[0]
            rawText = text

            if validators.url(text.lower()) or validators.url("http://"+text.lower()):
                textValidUrl = True
            else:
                textValidUrl = False

            if textValidUrl and not validators.url(rawUrl.lower()) and not validators.url("http://" + rawUrl.lower()) and url[0] != "#" and url[0] != "/":
                url = text.replace(" ", "").lower()
                text = rawUrl

            if url != None and text != None:
                if "http://" not in url and "https://" and not validators.url(url.lower()) and validators.url("http://"+url.lower()) and len(url) > 0 and len(text) > 0:
                    someBrokenLinks = True
                    url = "http://" + url.lower()
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

            if textValidUrl and not validators.url(rawUrl.lower()) and not validators.url("http://" + rawUrl.lower()) and url[0] != "#" and url[0] != "/":
                url = text.replace(" ", "").lower()
                text = rawUrl

            if url != None and text != None:
                if "http://" not in url and "https://" and not validators.url(url.lower()) and validators.url("http://"+url.lower()) and len(url) > 0 and len(text) > 0:
                    someBrokenLinks = True
                    url = "http://" + url
                    fixedUrls.append({"url": url, "mdLink":"["+text+"]("+url+")", "original":"("+rawText+")["+rawUrl+"]", "fixed":"\["+text+"\]\("+url+")"})




    if someBrokenLinks:

        message = '\n\n***\n^(I am a bot, and this action was performed automatically.)\n\n[^Feedback](https://np.reddit.com/message/compose?to=lucadem1313&subject=Link%20Fixer%20Bot "Contact to report issues, ask questions, or leave some feedback") ^| [^Formatting ^Help](https://np.reddit.com/wiki/commenting "Reddit.com markdown guide") ^| [^Subreddit](http://np.reddit.com/r/thelinkfixerbot "Subreddit for bot info")' # ^| [^Original ^Comment]('+pasteUrl+' "PasteBin of orinal comment")'

        commentText = "Uh-oh **"+c.author.name+"**, it looks like there's **"+str(len(fixedUrls))+"** broken markdown links in your post. I've listed them below:\n\nFixed Link | Original Markdown | Fixed Markdown\n:---------:|:----------:|:----------:"
        for link in fixedUrls:
            commentText += "\n" + link["mdLink"] + " | " + link["original"] + " | " + link["fixed"]
        commentText += message
        print c.id + "\n"
        if respond:
            while True:
                try:
                    reply = postThread.add_comment('[Original Comment]('+c.permalink.replace("/www.", "/np.")+')\n\n***\n\n>' + c.body.replace("\n", "\n>") + "\n\n***")
                    c.reply(commentText + ' ^| [^Original ^Comment]('+reply.permalink+' "Record of original comment")')
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
                except BaseException as error:
                    print 'Unknown error. Skipping.'
                    break



for c in praw.helpers.comment_stream(r, 'all'):
    if check_condition(c):
        bot_action(c, respond=True)
