
import facebook as fb
import pandas as pd
import requests, datetime, time, pickle, os, errno

SLEEP_TIME_SECONDS = 3 # Cooldown between API requests
MAX_COMMENTS_PER = 150 # Limit number of comments returned (0-100)
MAX_POSTS_PER = 1300  # Limit number of posts per page (1-???)

API_ID = '119664095335909'
API_SECRET = 'b904a3daab20b5592dc368f7d3921a04'

FB_PAGES = {
'postimees':'115634898452178',
'delfi':'183280829317',
'ohtuleht':'256434472932',
'paevaleht': '252655727907',
'eesti ekspress':'159041996650',
'maaleht': '159041996650',
'telegram': '452525991463873'
}


def login(id, secret):
    token = requests.get('https://graph.facebook.com/oauth/access_token?client_id={ID}&client_secret={SECRET}&grant_type=client_credentials'.format(
    ID=id,
    SECRET=secret)).json()
    return fb.GraphAPI(access_token=token['access_token'], version='2.7')

def load_object(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

def save_object(obj, directory, filename):
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with open('{}/{}.p'.format(directory, filename), 'wb') as f:
        pickle.dump(obj, f)

def read_comment(comment, post_id):
    d = {
        'created_time': comment['created_time'],
        'from_id': comment['from']['id'],
        'from_name': comment['from'].get('name'),
        'post_id': comment['id'],
        'message': comment['message'],
        'post_id': post_id
    }
    return d

def read_posts(posts, page_id, cache=True):
    df_posts = pd.DataFrame(posts['data'])

    # Flatten reactions into scalar value
    for c in [col for col in df_posts.columns if 'react' in col]:
        df_posts[c] = df_posts[c].apply(lambda x: x['summary']['total_count'])

    # Flatten shares into scalar value
    df_posts['shares'] = df_posts['shares'].apply(lambda x: 0 if pd.isnull(x) else x['count'])

    df_posts['page_id'] = page_id
    df_posts['scrape_time'] = datetime.datetime.now()

    # Rename id to post_id
    df_posts.columns = ['post_id' if c=='id' else c for c in df_posts.columns]


    # Separate comments to new DF
    comments = []

    for i,r in df_posts.iterrows():
        if not pd.isnull(r['comments']):
            [comments.append(read_comment(c, r['post_id'])) for c in r['comments']['data']]
    del df_posts['comments']

    df_comments = pd.DataFrame(comments)

    if cache:
        save_object(df_posts, 'posts', page_id)
        save_object(df_comments, 'comments', page_id)

    return df_posts, df_comments

def get_page_posts(page_id, post_limit=100, comment_limit=25, sleep_time=1.0):
    # https://stackoverflow.com/a/37276068
    reactions = ['LIKE','LOVE','WOW','HAHA','ANGRY','SAD']
    reactions_query = ','.join(['reactions.type({}).summary(total_count).limit(0).as(react_{})'.format(r, r.lower()) for r in reactions])
    fields_query = 'posts{{link,message,comments.limit({MC}),description,created_time,shares,{Q}}}'.format(MC=comment_limit, Q=reactions_query)

    posts = graph.get_object(id=page_id, fields=fields_query)['posts']
    save_object(posts,'debug', 'unknown')

    # Collect  each batch of comments / posts to a final output
    final_posts = pd.DataFrame()
    final_comments = pd.DataFrame()

    posts_read = 0

    while True:
        try:
            # Get initial batch
            posts_clean, comments_clean = read_posts(posts, page_id)

            # Count number read
            post_count = len(posts_clean)
            posts_read += post_count
            print('\tRead {} posts from feed...'.format(post_count))

            # Append results to the data frames
            final_posts = pd.concat([final_posts, posts_clean], axis=0, ignore_index=True)
            final_comments = pd.concat([final_comments, comments_clean], axis=0, ignore_index=True)

            # If the next read would keep us under post limit then try to get it
            if posts_read + post_count > post_limit:
                print('\tReached scrape limit...')
                time.sleep(sleep_time)
                break

            time.sleep(sleep_time)

            # Get the next batch of emails
            posts = requests.get(posts['paging']['next']).json()
        except KeyError:
            # Break if we don't have any next page to paginate to
            print('\tEnd of feed...')
            break
    return final_posts, final_comments

def scrape(pages, post_limit, comment_limit, sleep_time, cache=True, append=None):
    keys = list(pages.keys())
    print('Scraping {} pages...'.format(len(keys)))

    # Collect all comments and posts
    if append:
        final_df = load_object(append[0])
        final_comments = load_object(append[1])
    else:
        final_df = pd.DataFrame()
        final_comments = pd.DataFrame()

    i = 0
    for k in keys:
        # Loop through each page
        print('Scraping: {} - {} of {}'.format(k, i, len(keys)))
        try:
            df, df_comments = get_page_posts(pages[k], post_limit=post_limit, comment_limit=comment_limit, sleep_time=sleep_time)
        except:
            print('Scrape issue. Pausing for {} seconds and retrying once...'.format(5))
            time.sleep(5)
            df, df_comments = get_page_posts(pages[k], post_limit=post_limit, comment_limit=comment_limit, sleep_time=sleep_time)

        final_df = pd.concat([final_df, df], axis=0, ignore_index=True)
        final_comments = pd.concat([final_comments, df_comments], axis=0, ignore_index=True)
        i+=1

    finish_time = '{}'.format(datetime.datetime.now()).replace('.','_').replace(':','_')
    print('Completed scrape at {}...'.format(finish_time))

    if cache:
        print('Final results cached at /final...')
        save_object(final_df, 'final', 'posts_{}'.format(finish_time))
        save_object(final_comments, 'final', 'comments_{}'.format(finish_time))
    return final_df, final_comments


if __name__ == "__main__":
    graph = login(API_ID, API_SECRET)

    # If appending a previous run, use a tuple like the following:
    # append=('final/posts_2017-07-14 12_44_05_229587.p','final/comments_2017-07-14 12_44_05_229587.p')
    df_posts, df_comments = scrape(FB_PAGES, MAX_POSTS_PER, MAX_COMMENTS_PER, SLEEP_TIME_SECONDS, cache=True, append=None)



