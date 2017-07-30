# Facebook News Scraper

## Overview
Dataset contains **5250** posts from **6** various news organizations & personalities representing up to the last page posts made as of July 29th, 2017. Each post has up to 100 comments for a total of **32399** comments.

## Files
- post\_scraper\_ee.py - script used to scrape pages
- Estonian FB analuus.ipynb - in final directory where analysis is shown


## Script
This script loops though a dictionary of Facebook page ids and retrieves the last N posts and up to 100 comments for each post. The results are optionally cached as individual data files and ultimately stored as a set of data frames: one for posts, one for comments. They can be linked by the common post_id field.

While originally used for news sites, this script can accommodate any Facebook page. One could also loop though the comments to get more than the last 100.
If you want to get FB page page_id, just select *View Source* in your browser, and make search by *page_id*.
## Fields - Posts
- created\_time
- description: only for posts with links
- link
- message: post contents
- page\_id
- post\_id
- react\_angry
- react\_haha
- react\_like
- react\_love
- react\_sad
- react\_wow
- scrape\_time
- shares

## Fields - Comments
- created_time
- from_id: user id
- from_name: publicly visible name of poster
- message
- post\_id: parent post\_id

## Pages Scraped
May be subject to future additions.
'postimees':'115634898452178',
'delfi':'183280829317',
'ohtuleht':'256434472932',
'paevaleht': '252655727907',
'eesti ekspress':'159041996650',
'maaleht': '159041996650',
'telegram': '452525991463873'


