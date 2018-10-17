
# Importing required libraries from Python3 
import urllib.request
from bs4 import BeautifulSoup
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

# Information about the current Date-Month-Year
now = datetime.datetime.now()

# Taking the Input of Email-Id
email = input('Enter your EmailId: ')

# Taking the Input of the names of TV Series
series_input= input('TV Series: ')

# Retriving the name of the TV Series considering the case that the name are separated by commas.
tvseries=[str(x) for x in series_input.split(',')]

# This function is used to convert the date information received from IMDB Scrapper into the YYYY-MM-DD format
def convert_in_format(st_date):
    arr=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    year_con=st_date[-4:]
    #Because May is the only Month with 3 letters,therefore it does not has '.' in it.
    if(st_date[-6]=='y'): 
        month_con=st_date[-8:-5]
        date_con=st_date[:-9]
    else:
        month_con=st_date[-9:-6]
        date_con=st_date[:-10]
    month_index=arr.index(month_con)+1
    dt_format=str(year_con)+"-"+str(month_index)+"-"+str(date_con)
    return dt_format

# This function is used to compare the date send in parameter, whether it is in future or has passed.
def compare_date(date_com):
    date_year,date_month,date_date= map(lambda x: int(x), convert_in_format(date_com).split('-'))
    dt = datetime.datetime(date_year, date_month, date_date) 
    dtoday = datetime.datetime(now.year, now.month, now.day) 
    if(dt>dtoday):
        return 1
    elif(dt<dtoday):
        return -1
    else:
        return 0

# This variable is used to concatenate the information which is being send through the Mail.
finalresult=''   
# This loop runs the number of TV series entered by the User.

Name_Series=''
count=0
for tvslist in tvseries:
    
    # If the Name of the TV Series is more than one word.
    passname=tvslist.strip().replace(' ','+')
    # Scrapping the information of the First TV Series named in the page.
    baseurl='https://www.imdb.com/find?ref_=nv_sr_fn&q='+passname+'&s=all'
    tvslink1='https://www.imdb.com'+BeautifulSoup(urllib.request.urlopen(baseurl).read(),
                            'html.parser').find_all(class_ = "result_text")[0].a.get('href')
    print(tvslink1)
    
    # Scrapping the information of the latest Season of that TV Series
    soap_tvslink1=BeautifulSoup(urllib.request.urlopen(tvslink1).read(),'html.parser')
    title_name=soap_tvslink1.find_all(class_ = "title_wrapper")[0].h1.get_text() 
    tvslink2='https://www.imdb.com'+soap_tvslink1.find_all(class_ = "seasons-and-year-nav")[0].a.get('href')
    
    # Scrapping the dates of the episode which are going to be air
    print(tvslink2)
    dates=BeautifulSoup(urllib.request.urlopen(tvslink2).read(),
                            'html.parser').find_all(class_ = "airdate")
    s_da_unf=[]
    result=''
    if(count<(len(tvseries)-1)):
        count=count+1
        Name_Series=Name_Series+title_name.strip()+', '
    else:
        Name_Series=Name_Series+title_name.strip()
        
    # Extracting only the Dates information and storing in a list or further ease of work
    for x in dates:
        s_da_unf.append(x.get_text().strip())
    
    # This if condition of that condition when the Season is going Air next year and exact date not provided 
    if(now.year < int(s_da_unf[0][-4:]) and len(s_da_unf[0])==4):
        result=' The next season begins in '+s_da_unf[0][-4:]
        
    # This condition is of the case when Season will begin next year and dates are provided
    elif(now.year < int(s_da_unf[0][-4:]) and len(s_da_unf[0])>4):
        result=' The next season begins in '+convert_in_format(s_da_unf[0])
        
    # This condition is of the case when the Season will begin streaming this year and dates are confirmed
    elif(now.year == int(s_da_unf[0][-4:]) and len(s_da_unf[0])>4 and compare_date(s_da_unf[0])>-1):
        result='The next season will begins in '+convert_in_format(s_da_unf[0])
        
    # This condition is of the case when the Season will begin this year but dates not confirmed
    elif(now.year == int(s_da_unf[0][-4:]) and len(s_da_unf[0])==4):
         result='The next season will begin this year but date not confirmed'
            
    # This is the condition when the Season has begin and has not ended, i.e. More episode to come
    elif(now.year == int(s_da_unf[0][-4:]) and compare_date(s_da_unf[0])==-1):
        i=0
        while(i<=(len(s_da_unf)-1)):
            if(len(s_da_unf[i])>4):
                if(compare_date(s_da_unf[i])>-1):
                    result='The next episode airs on '+convert_in_format(s_da_unf[i])
                    break     
            else:
                result='The date of next episode is not informed'
                break
            i=i+1
            
    # This is the condition when the Season has begin streaming this year and has also ended.
    elif(now.year == int(s_da_unf[len(s_da_unf)-1][-4:]) and compare_date(s_da_unf[len(s_da_unf)-1])==-1):
        result='The show has ended has finished streaming all its episodes this year'
        
    # This is the condition when Season has already ended before this year.
    elif(now.year > int(s_da_unf[len(s_da_unf)-1][-3:])):
        result='The show has finished streaming all its episodes.'

    print(result)
    finalresult=finalresult+'Tv series name: '+'<a href="'+tvslink1+'">'+title_name.strip()+"</a>"+'<br>'+'Status: '+result+'<br><br>'

db = pymysql.connect("localhost","root","password","root")
cur = db.cursor()
s_comm1 = "Create database [IF NOT EXISTS] TVSeries"
try:
    cur.execute(s_comm1)
    db.commit()
except:
    db.rollback()
s_comm2 = "use TVSeries"       
try:
    cur.execute(s_comm2)
    db.commit()
except:
    db.rollback()
       
s_comm3 = "create table [IF NOT EXISTS] record(email varchar(100), series varchar(550))"       
try:
    cur.execute(s_comm3)
    db.commit()
except:
    db.rollback()

s_comm4 = "INSERT INTO record VALUES ('%s', '%s' )" % (email, Name_Series)      
try:
    cur.execute(s_comm4)
    db.commit()
except:
    db.rollback()

db.close()


# Sending Mail through the mail id, Sometimes you need to allow Low-security application allowance features
msg = MIMEMultipart()
msg['From'] = "16ucc070@lnmiit.ac.in" #Replace this mail id with your Email id
msg['To'] = email
msg['Subject'] = "TV-Series Episode Details"
SUBJECT = "TV-Series Episode Details"
TO = email
FROM = "16ucc070@lnmiit.ac.in" #Replace this mail id with your Email id
msg.attach(MIMEText(finalresult,'html'))

server = smtplib.SMTP('smtp.gmail.com')
server.starttls()
server.login('16ucc070@lnmiit.ac.in', 'password') #Replace this mail id with your Email id
server.sendmail(FROM, [TO], msg.as_string())
server.quit()
