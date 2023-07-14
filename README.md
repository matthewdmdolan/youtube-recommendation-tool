# Youtube Recommendation Tool 

# Introduction

The motivation in building this model broadly lies with my disatisfaction with the dynamics of the emergent attention economy. After watching The Social Dilemma documentary, I removed myself from most forms of social media, due to concerns around what it was doing to my attention span, alongside data privacy concerns. However, after this I found I was wasting a lot of time watching videos on Youtube. 

There is a well developed notion in the public lexicon of Youtube and its contribution towards the emergence of the attention economy, or even creation according to some critics (source: https://www.newyorker.com/books/under-review/the-overlooked-titan-of-social-media), Therefore, I wanted to try and build a model that utilises the Youtube API to identify the most important sources of content for me, across a range of topics. I use it for a number of different hobbies, namely: coding, powerlifting, music mixes. Therefore, the development of a model that allows me to do this would save me a significant amount of time. Initially, the repo is just trying to find disco music mixes that will stop me from wasting many hours trying to find new music. 

# Data

Youtube API V3 - Source: https://developers.google.com/youtube/v3/docs

Annoyingly, the Youtube API V3 has removed some features that would allow for an easier development process. This includes being able to access your own user history. Moreover, youtube as a website have removes dislikes which would have provided an essential tool in being able to control for 'clickbait' videos. However, we will be able to use NLP methods on comments in order to assess any levels of dissatisfaction with the content of the video. How well this will work is another question: I've seen youtube comment sections degrade into hotly contested debates about the existence of a higher power on a video of a cat playing a keyboard, so it will be interesting to see the influence of that input within our model.  

# Development 

Ultimately, the initial model development involved utilising multiple kpis to try and control for various contextual factors. Here are the KPIS and their subsequent definitions:

1. Views per Day = viewcount / days since sublished
2. Engagement Rate = (likes + comments) / viewcount
3. Engagement per Day = (likes + comments) / Viewcount
4. Performance KPI =  (weight_views * ViewCount) + (weight_likes * Likes) + (weight_favourites * Favourites) + (weight_comments * Comments)

Accounting for virality: 
1. Viral Score = viewcount * engagement rate
2. Views per day exponential weighted moving average = Mean weighted 7 day average of views per day
(was worried the moving a moving average might smooth over the weighted average too much, meaning we would lose the identifiying factors of video virality)
3. Days since published decay = (decay rate ** days since published)
  (decay rate is defined locally, e.g. 0.95)
5. Views decay adjusted =  viewcount / days since published decay
   

# Critical Analysis 


