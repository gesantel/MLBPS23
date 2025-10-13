# MLBPS23

Find the substack article [here](https://georgesantellano.substack.com/p/quantifying-what-we-all-saw-coming). 

The objective of this project was originally to study the 2023 performance of the Arizona Diamondbacks. 
I wanted to answer what hitting statistics made them so successful in that year's playoff runs. Read more about the turns this project took in the substack article. 
This was a portfolio project so I emphasized showcasing skills more so then practicality so my data processing for example is overkill but it demonstrates ability in a lot of techniques.  

Tools used: StatsAPI, pandas, sklearn (scikit-learn), matplotlib, seaborn. 

Features: xbh rate, extra base hits, obp, slug, stolen bases, walks, strike outs, home runs, triples, doubles, team. 

Target variable: runs. 

## Data Collection
I used MLB-StatsAPI to gather data. 

## Data Processing
I used sklearn train_test_split to split my training and validation data. I used OneHotEncoding, StandardScaler, in pipelines for my numerical and categorical columns. I bundled their preprocessing with ColumnTransformer and then used a Pipeline to bundle my preprocessing and my model. 

## Model and Fitting
I used sklearn RandomForestRegressor with n_estimators = 100 and set a random state. 

##Postseason package
I created a postseason.py package to generalize the data collection using the functions 
get_abbreviation, get_postseason_teams_by_year, and get_postseason_hitting_by_year

so that anyone can quickly build a postseason hitting dataset by importing it, and calling get_postseason_hitting_by_year(year).


