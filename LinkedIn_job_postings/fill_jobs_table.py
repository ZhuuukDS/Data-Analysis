import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import csv
import random
import time
import re
import pyodbc



def run_scrap_jobs():

    server = 'linkedin-parsed-database.cqnzuwvuvkve.us-west-1.rds.amazonaws.com, 1433'
    database = 'test_db'
    username = 'admin'
    password = '********'

    today = date.today() # returns the current local date
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    }


    def get_links_to_jobs(headers):
        for i in range(0, 1025, 25): # there are 40 pages available with 25 jobs on each page.
            url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Data&location=Israel&locationId=&geoId=101620260&f_TPR=r604800&start={i}'
            resp = requests.get(url, headers=headers)
            soup = BeautifulSoup(resp.content, 'lxml')

            if len(soup.text): # if the page is not empty
                # find all the links to job pages
                all_links = soup.find_all('a', class_='base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]')
                # and save them in the .txt file
                with open(f'data/{today}_links_to_jobs.txt', 'a') as file:
                    [print(link.get('href'), file=file) for link in all_links]

        print(f'All links saved to "{today}_links_to_jobs.txt" file')
        
     
    get_links_to_jobs(headers)
     
     
    with open(f'data/{today}_jobs.csv', 'a', newline='',  encoding='utf-8') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['job_title',
                         'posting_date',
                         'company_name',
                         'location',
                         'seniority_level',
                         'employment_type',
                         'job_function',
                         'industries',
                         'job_description'])
                         
                         

    # Now let's get the info from each job page and save it the file
    with open('data/all_jobs.csv', 'a', newline='', encoding='utf-8') as output_file, \
            open(f'data/{today}_links_to_jobs.txt', 'r') as input_file, \
            open(f'data/{today}_jobs.csv', 'a', newline='', encoding='utf-8') as today_output_file:
        writer = csv.writer(output_file)
        writer2 = csv.writer(today_output_file)
        print(f'Parsing data from links from file: \'data/{today}_links_to_jobs.txt.....')
        links = input_file.readlines()
        for line in links:
            #time.sleep(random.randint(1,3))
            line = line.replace('il', 'www').strip()
            try:
                resp = requests.get(line, headers=headers)
            except:
                time.sleep(5)
                resp = requests.get(line, headers=headers)
                    
            # check the request
            #time.sleep(2)
            if resp.status_code == 200: 
                print(f'{resp} ---> Everything\'s OK! ---> Parsing....')
            else:
                print(f'{resp}Something went wrong!.....')
                continue
                
            # let's parse! 
            soup = BeautifulSoup(resp.content, 'lxml')

            # job_title
            job_title = soup.find('h1').text.strip()

            # company_name
            company_name = soup.find('span', class_='topcard__flavor').find('a').text.strip()

            # location
            try:
                location = soup.find('span', class_='topcard__flavor topcard__flavor--bullet').text.strip()
            except:
                location = 'Unknown'
            # posting_date
            try:         
                n_days_ago = int(soup.find('span', class_= 'posted-time-ago__text topcard__flavor--metadata').text.strip().split()[0])
                posting_date = today - timedelta(days = n_days_ago)
            except:
                posting_date = today

            # job_description
            job_description = soup.find('div', class_='show-more-less-html__markup').text.strip()

            # seniority_level, employment_type, job_function, industries 
            job_criterias = soup.find_all('span', class_='description__job-criteria-text description__job-criteria-text--criteria')
            criterias = [criteria.text.strip() for criteria in job_criterias]
            # save them separately in variables:

            #seniority_level
            try:
                seniority_level = criterias[0]
            except:
                seniority_level = "Unknown"

            # employment_type
            try:
                employment_type = criterias[1]
            except:
                employment_type = "Unknown"

            # job_function
            try:
                job_function = criterias[2]
            except:
                job_function = "Unknown"

            # industries
            try:
                industries = criterias[3]
            except:
                industries = "Unknown"
            
            # write row in the file
            writer.writerow([job_title, posting_date, company_name, location, seniority_level, employment_type, \
                         job_function, industries, job_description])
            writer2.writerow([job_title, posting_date, company_name, location, seniority_level, employment_type, \
                         job_function, industries, job_description])
        print('Completed!')          

    time.sleep(10)

    data = pd.read_csv(f'data/{today}_jobs.csv')

    # the list of modern data skills (retrieved from data job descriptions)
    skills = ['airflow', 'bokeh', 'zeppelin', 'scikit-learn', 'seaborn', 'pyspark', 'analyze', 'powerpoint', 'dbs', 'informatica', 'mulesoft', 'pipelines', 'keras', 'hdfs', 'databricks', 'datadog', 'cloud', 'ml', 'rapidminer', 'mstr', 'apachenifi', 'server', 'knime', 'js', 'asana', 'prometheus', 'powerbi', 'scipy', 'pipeline', 'oltp', 'golang', 'flourish', 'hive', 'kubernetes', 'qlikview', 'industrial', 'dynamodb', 'mining', 'scala', 'kotlin', 'docker', 'elasticsearch', 'redshift', 'sap', 'mongodb', 'analysis', 'english', 'cassandra', 'dashboards', 'dataddo', 'dba', 'cypress', 'snowflake', 'spark', 'testim', 'datawrapper', 'nltk', 'h2o.ai', 'tableau', 'economics', 'elt', 'mathematics', 'powerquery', 'mapreduce', 'bigquery', 'synapse', 'ai', 'azure', 'dvc', 'athena', 'jupyter', 'dashboard', 'javascript', 'vba', 'mlops', 'groovy', 'postgres', 'hebrew', 'c', 'apis', 'dataflow', 'db', 'd3.js', 'nlp', 'tensorflow', 'elk', 'airtable', 's3', 'qa', 'apache-beam', 'etl', 'lakehouse', 'gensim', 'terraform', 'github', 'spring', 'collibra', 'programming', 'neo4j', 'olap', 'dataform', 'parquet', 'googlecloud', 'apache-nifi', 'database', 'rac', 'dl', 'rectlabel', 'sqs', 'sql', 'r', 'redis', 'pypi', 'statistics', 'scrum', 'reports', 'algorithms', 'java', 'python', 'matplotlib', 'git', 'dwh', 'jira', 'plotly', 'mysql', 'computer-vision', 'streamsets', 'apache', 'excel', 'nodejs', 'saas', 'mlflow', 'json', 'linux', 'dax', 'kinesis', 'labelbox', 'presto', 'aws', 'api', 'gcp', 'kubeflow', 'adls', 'talend', 'oracle', 'vertica', 'cognos', 'conda', 'alation', 'hbase', 'hadoop', 'bigdata', 'math', 'pytorch', 'kafka', 'marketing', 'nosql', 'microstrategy', 'numpy', 'coding', 'pandas', 'glue', 'datarobot', 'julia', 'looker', 'sklearn', 'visualization', 'ab', 'cli', 'snappy', 'automl', 'perl', 'matlab', 'html']
    skills = list(set(map(str.lower, skills)))


    # data cleaning function
    def data_cleaning(data, skills):
        df = data.copy()
        print(df.shape)
        
        # cleaning job_names
        
        df = df[df['job_title'].str.contains('Data|Analyst|Analysis|Scientist|BI|SQL|ML|AI|Machine Learning|Data Science')]
        print(df.shape)
        df.insert(1, 'generalized_job_name', np.where(df['job_title'].str.contains('ML Engineer|Machine Learning|AI', flags=re.IGNORECASE), 'ML/AI Engineer', df['job_title']))
        df = df[~df['generalized_job_name'].str.contains('Software Engineer|Backend Engineer|Director|DevOps', case=False)]
        df['generalized_job_name'] = np.where(df['job_title'].str.contains('Analyst|Analysis|SQL|Analytics', flags=re.IGNORECASE), 'Data Analyst', df['generalized_job_name'])
        df['generalized_job_name'] = np.where(df['job_title'].str.contains('BI ', flags=re.IGNORECASE), 'BI Developer', df['generalized_job_name'])
        df['generalized_job_name'] = np.where(df['job_title'].str.contains('Data.*Engineer|Database|Big Data|Infrastructure|Architect', flags=re.IGNORECASE, regex=True), 'Data Engineer', df['generalized_job_name'])
        df['generalized_job_name'] = np.where(df['job_title'].str.contains('Science|Scientist', flags=re.IGNORECASE), 'Data Scientist', df['generalized_job_name'])
        generalized_job_names = ['Data Analyst', 'Data Scientist', 'BI Developer', 'Data Engineer', 'ML/AI Engineer']
        df = df[df['generalized_job_name'].isin(generalized_job_names)]
        df = df.drop_duplicates()
        print(df.shape)
        
        # getting experience and cleaning description
        
        def keep_requirements(text):
            experience = re.compile('[1-9]\s{0,1}\+{0,1}\s[Yy]ears')
            if 'Requirements' in text:
                text = text.split('Requirements')[1]
                if experience.findall(text):
                    exp_years = max(experience.findall(text))
                else:
                    exp_years = 'Unknown'

            elif experience.findall(text):
                exp_years = max(experience.findall(text))
                text = re.split(r'[1-9]\s{0,1}\+{0,1}\s[Yy]ears', text, 1)[1]
            else:
                text = text
                exp_years = 'Unknown'
        
            return (exp_years, text)
        
        df['job_description'] = df['job_description'].apply(keep_requirements)
        
        # separate description and required years of experience column
        df['experience'] = df['job_description'].apply(lambda x: x[0])
        df['description'] = df['job_description'].apply(lambda x: x[1])
        # remove spaces between number and '+'
        #df['experience'] = df['experience'].apply(lambda x: re.sub(r'(?<=\d)\s+(?=\D{1,2}(\s|$))','', x))
        df['experience'] = df['experience'].apply(lambda x: x[0]+'+' if x[0] != 'U' else x)
        
        # transform description
        
        def clean_text(text, skills=skills):
                text = re.sub(r'[^\x00-\x7f]', r'', text) # only latin
                text = text.replace('A/B', ' AB ')
                text = text.replace('SQL', ' SQL ')
                text = text.replace('ETL', ' ETL ')
                text = re.sub(':[/\(\).]', ' ', text)
                text=re.sub("(\\d|\\W)+"," ", text) # remove special characters and digits
                text = re.sub('\s+',' ', text) # remove whitespace and newlines
                # add space between last lowercase letter and first Uppercase letter
                text = re.sub('([a-z])([A-Z])', r'\1 \2', text)
                # deal with double words
                text = re.sub('[Pp]ower [Bb][Ii]', ' PowerBI ', text)
                text = re.sub('[Nn]atural [Ll]anguage [Pp]rocessing', ' NLP ', text)
                text = re.sub('[Mm]achine [Ll]earning', ' ML ', text)
                text = re.sub('[Dd]eep [Ll]earning', ' DL ', text)
                text = re.sub(' [Bb][Ii] ', ' PowerBI ', text)
                text = re.sub('[Mm]y [Ss][Qq][Ll]', ' MySQL ', text)
                text = re.sub('[Nn]o [Ss][Qq][Ll]', ' NoSQL ', text)
                text = re.sub('[Qq]lik [Vv]iew', ' QlikView ', text)
                text = re.sub('[Bb]ig [Dd]ata', ' BigData ', text)
                text = re.sub('[Mm]ongo [Dd][Bb]', ' MongoDB ', text)
                text = re.sub('[Gg]oogle [Cc]loud', ' GoogleCloud ', text)
                text = re.sub('[Dd]ata [Ww]arehousing', ' DWH ', text)
                text = re.sub('[Aa]rtificial [Ii]ntelligence', ' AI ', text)
                text = re.sub('[Bb]ig [Qq]uery', ' BigQuery ', text)
                text = re.sub('[Pp]ower [Qq]uery', ' PowerQuery ', text)
                text = re.sub('[Mm]ap [Rr]educe', ' MapReduce ', text)
                text = re.sub('[Dd]ynamo [Dd][Bb]', ' DynamoDB ', text) 
                text = re.sub('[Bb]usiness [Ii]ntelligence', 'PowerBI', text)
                text = re.sub('[Cc]omputer [Vv]ision', 'Computer-Vision', text)
                text = re.sub('[Ss]ci[Kk]it [Ll]earn', 'SciKit-Learn', text)
                text = re.sub('[Aa]pache [Bb]eam', ' Apache-Beam ', text)
                text = re.sub('[Aa]pache [Nn]i[Ff]i', 'Apache-NiFi', text)
                # remove punctuation
                text = ", ".join(list(set([word for word in text.split() if word.lower() in skills])))
                return text.strip()
        
        # remove, rename, save
        df['description'] = df['description'].apply(lambda x: clean_text(x, skills))
        df.drop(['job_description', 'job_title'], axis=1, inplace=True)
        df.rename(columns = {'generalized_job_name': 'job_title',
                             'description': 'skills' }, inplace=True)
        df.drop_duplicates(inplace=True)
        df = df.fillna('NA')
        #df.to_csv('data/final_table.csv', index=False, header=False, mode='a')
        
        return df



    last_df = data_cleaning(data, skills)    


    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()

    list_of_tuples = [tuple(x) for x in last_df.to_records(index=False)]

    insert_query = "INSERT INTO jobs (job_title, posting_date, company_name, location, seniority_level, employment_type, job_function, industries, experience, skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


    for row in list_of_tuples:
        try:
            cursor.execute(insert_query, row)
        except pyodbc.DataError as e:
            print("Error inserting row:", row)
            print("Error message:", e)


    # Commit the changes
    cnxn.commit()

    cursor.close()
    cnxn.close()
    print('Done')



if __name__ == '__main__':
    run_scrap_jobs()