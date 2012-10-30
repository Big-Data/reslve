
RESLVE system has following 8 algorithms.

==========
7 VSM algorithms that compare overlap of following features of the user's articles
and a candidate's article. These algorithms can compute similarity via both gensim 
library or our implemented tdmatrix; currently the gensim lib is being used. 

(article centric)
- RESLVE_ArticleContentBowVsm: Measures similarity between the BOW of a candidate resource’s article content
							   and the BOW built from all the edited articles in the user’s interest model.
- RESLVE_ArticleIdVsm: Similarity based on a candidate article’s ID overlapping with the user’s
					   edited articles’ IDs. In other words, this will only result in non-zero similarity
					   scores for candidates that correspond to articles the user has edited.
- RESLVE_ArticleTitleBowVsm: Similarity based on how many words in a candidate article’s title overlap
							 with words in titles of articles the user has edited.

(direct categories centric)
- RESLVE_DirectCategoryIdVsm: Like Article_ID_VSM but similarity depends on IDs of the categories of a
							  candidate article and user’s articles overlapping. The idea is that generalizing
							  entity concepts up to the category level will increase potential for overlap.
- RESLVE_DirectCategoryTitleBowVsm: Similarity based on the candidate article’s category titles BOW and the
									user’s articles’ category titles BOW.

(category hierarchy centric)
- RESLVE_GraphCategoryIdVsm: Same as DirectCategoryIdVsm but incorporates all categories in
							 the hierarchy originating from a candidate article or user article
- RESLVE_GraphCategoryTitleBowVsm: Same as DirectCategoryTitleBowVsm but incorporates all categories in
							 	   the hierarchy originating from a candidate article or user article

==========
Also have a WSD algorithm. 
- RESLVE_ArticleContentBow_Wsd: selects as an entity's correct candidate resource the one that 
								is most frequently the top ranked candidate for all resolutions 
								of the entity that occur in the user's set of edited articles.
