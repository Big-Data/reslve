
RESLVE system has following 8 algorithms.

==========
7 VSM algorithms that compare overlap of following features of the user's articles
and a candidate's article. These algorithms can compute similarity via both gensim 
library or our implemented tdmatrix; currently the gensim lib is being used. 

(article centric)
- RESLVE_ArticleContentBowVsm: BOW of article page content
- RESLVE_ArticleIdVsm: BOW of article title
- RESLVE_ArticleTitleBowVsm: article ID

(direct categories centric)
- RESLVE_DirectCategoryIdVsm: BOW of titles of article's direct categories
- RESLVE_DirectCategoryTitleBowVsm: IDs of article's direct categories

(category hierarchy centric)
- RESLVE_GraphCategoryIdVsm: IDs of categories present in article's category hierarchy
- RESLVE_GraphCategoryTitleBowVsm: BOW of category titles present in article's category hierarchy

==========
Also have a WSD algorithm. 
- RESLVE_ArticleContentBow_Wsd: selects as an entity's correct candidate resource the one is
most frequently the top candidate in rankings for that entity in the user's edited articles
