## The Data-related Job Postings on LinkedIn Israel

I am pleased to announce that I have finally completed a big project that involved collecting, storing and analyzing data on job positions opened in LinkedIn Israel. 
This project required extensive data collection, cleaning, transformation, and storage in a cloud database, which was then used to generate a real-time report in Power BI.

So, what I've done?

1. Wrote a Python script to parse information about data-related job postings from LinkedIn
2. Created an AWS EC2 instance and loaded the Python script onto the instance
3. Configured a cron job on the EC2 instance to automatically run the script every Sunday to gather new postings
4. Created an AWS RDS database with the Microsoft SQL Server engine
5. Created a table in the RDS database to store the job information and keep updating the table on a weekly basis with new entries
6. Connected the Python script on the EC2 instance to the RDS database to update the job information in the table
7. Connected to RDS database using Azure Data Studio to check the data correctness
8. Used Power BI to connect to the RDS database and made data transformations with Power Query
9. Designed a Power BI report that provided job market insights and helped make decisions about job opportunities in the data field

Overall, this project was a significant undertaking, and I am proud of the work that I have accomplished. 

https://user-images.githubusercontent.com/93790312/231987257-05215cbd-8f25-45a5-9201-7d0de91368c8.mp4

