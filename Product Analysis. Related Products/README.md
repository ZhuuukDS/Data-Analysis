## Product Data Analysis. Related Products

<img src='data/action.png'>

#### Task Formulation

Some categories in the product range are related. For example, phone accessories are useless without the phones themselves. Therefore, for promotions, mailings, and recommendations, it is important to know the existence of this kind dependencies between categories and in categories with themselves (if users access the category repeatedly). What are the dependencies, and between which categories, if we consider only purchases? How does the user behave when browsing products? How are purchases fundamentally different from views, and why?
Find insights, with explanations. Graphics are welcome.

#### Data Description

We are given a dataset from a online shop's related database. This dataset contains data about users behavior and product catalog:

- product views
- category views
- product purchases
- lists of products and categories

The sample was formed only from sessions of users who looked at product pages at least 3 times, or bought any product. The dataset was created on the basis of historical records for the last 6 months in such a way that all existing dependencies and distributions are preserved, but there is no information in the dataset about the sequence of visiting by a particular person.

The data is anonymized. Session, order and product IDs have been replaced with hashes. A monotonic transformation is applied to the cost of goods in such a way that the ratio between the prices of goods is preserved. Category IDs and their names, as well as product brands, are not modified.

The dataset provides all the necessary categories that are in the catalog, as well as information about purchased and part of non-purchased goods.


### You can check [pdf](data/related_products.pdf) version and a [Jupyter Notebook](related_products.ipynb) with full analysis and conclusion.


