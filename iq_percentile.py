import praw
import re
import random
from scipy.stats import norm


starters = ["Golly Gee! ", "Wowza! ", "Sweet Butter Crumpets! ", "Gasp! ", "Sweet Baby Jesus! ",
            "Incredible! ", "Holy Moly! ", "By Jove! ", "Gee Willikers! ", "Gazooks! ", "Aw Lordy!"]

# Feel free to suggest additional regex patterns to match
# patterns = {"iq is/of xxx", "xxx iq"}
patterns = {"iq (of|is) [0-9]+(,[0-9]+)?", "[0-9]+(,[0-9]+)?\s?iq"}

# Running list of comments (locally stored only) I've already replied to. Manually CTRL-A-DEL'ed periodically
replied_to_write = open("repliedto.txt", "a")

replied_to_read = [line.rstrip() for line in open("repliedto.txt", "r")]


def login():
    reddit = praw.Reddit("iq_percentile")
    return reddit


def run_bot(r, visited):
    subreddit = r.subreddit("iamverysmart")
    num_posts = 20

    for submission in subreddit.hot(limit=num_posts):
        submission.comments.replace_more(limit=0)
        comment_list = submission.comments.list()

        for comment in comment_list:
            if comment.permalink() in visited:
                continue
            reply_to_comment(comment)

def sci_notation(number, sig_fig=8):
    ret_string = "{0:.{1:d}e}".format(number, sig_fig)
    a,b = ret_string.split("e")
    b = int(b) #removed leading "+" and strips leading zeros too.
    return a + " * 10^" + str(b)
            
def reply_to_comment(comment):
    for pattern in patterns:
        text = str(comment.body)
        regex = re.search(re.compile(pattern, re.IGNORECASE), text)
        if regex:
            print(regex.group(0) + "\n" + text + "\n" + comment.permalink() + "\n\n")

            # Calculate percentile from extracted the integer in the matched string
            # Gets percentile of first number in regex group (there will only be one by definition of the pattern)
            iq = int(re.findall("\d+,?\d+?", regex.group(0))[0])
            num = norm.cdf(iq, 100, 15)
            if num == 1:
                num = norm.cdf(iq, 100, 15)
                if num == 0:
                    comment.reply(random.choice(starters) + "That's so smart I can't even find a percentile for it!"
                                                        "\n\n ^Code: ^https://github.com/kcdode/iq_percentile")
                else:
                    written_number = sci_notation(num)
                    comment.reply(random.choice(starters) + "That IQ is in the top" + written_number +
                              " percent of people!" +
                              "\n\n ^Code: ^https://github.com/kcdode/iq_percentile")
            elif num < 0.5:
                comment.reply(random.choice(starters) + "That IQ suggests a truly feeble mind!" +
                              "\n\n ^Code: ^https://github.com/kcdode/iq_percentile")
            else:
                comment.reply(random.choice(starters) + "That IQ is in the " + str(num*100) +
                              "th percentile of people!" +
                              "\n\n ^Code: ^https://github.com/kcdode/iq_percentile")

            replied_to_write.write(comment.permalink())
            replied_to_write.write("\n")


run_bot(login(), replied_to_read)
