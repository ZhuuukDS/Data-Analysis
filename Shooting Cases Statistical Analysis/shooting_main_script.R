library(ggplot2)
library(dplyr)
library(lubridate)

original_data <- read.csv('https://data.cityofnewyork.us/api/views/833y-fsy8/rows.csv?accessType=DOWNLOAD')

str(original_data)

cleaned_df <- original_data %>%
  select(-c(INCIDENT_KEY, OCCUR_TIME, PRECINCT, JURISDICTION_CODE, LOCATION_DESC, X_COORD_CD, Y_COORD_CD, Latitude, Longitude, Lon_Lat)) %>%
  rename(Date = OCCUR_DATE, Area = BORO, Murdered = STATISTICAL_MURDER_FLAG) %>%
  mutate(Murdered = if_else(Murdered == 'true', 1, 0),
         PERP_SEX = if_else(PERP_SEX == '', 'UNKNOWN', PERP_SEX),
         PERP_RACE = if_else(PERP_RACE == '', 'UNKNOWN', PERP_RACE),
         PERP_AGE_GROUP = if_else(PERP_AGE_GROUP %in% c('', '224', '1020', '940'), 'UNKNOWN', PERP_AGE_GROUP))

cleaned_df$PERP_RACE[cleaned_df$PERP_RACE == 'AMERICAN INDIAN/ALASKAN NATIVE'] <- 'AM. INDIAN/ALASKAN'
cleaned_df$VIC_RACE[cleaned_df$VIC_RACE == 'AMERICAN INDIAN/ALASKAN NATIVE'] <- 'AM. INDIAN/ALASKAN'
cleaned_df$Date <- mdy(cleaned_df$Date)
cols <- c('Area', 'PERP_AGE_GROUP','PERP_SEX', 'PERP_RACE', 'VIC_AGE_GROUP', 'VIC_SEX', 'VIC_RACE')
cleaned_df[cols] <- lapply(cleaned_df[cols], factor)

str(cleaned_df)

p <- theme(axis.text.x = element_text(color="#993333", size=5, angle=90),
           axis.text.y = element_text(face="bold", color="#993333", size=5),
           legend.text = element_text(size=10),
           title = element_text(face='bold', size=10))



# Cases per day
cleaned_df %>%
  group_by(Date) %>%
  summarize(Cases = n()) %>%
  ggplot(aes(x = Date, y = Cases))+
  geom_point(size=.3, color='blue')+
  ggtitle('Shooting Incidents Per Day')+
  scale_x_date(date_breaks = "1 year", date_labels = "%Y") +
  theme(axis.title.x=element_blank(),
        axis.text.x = element_text(color="#993333", size=5),
        axis.text.y = element_text(face="bold", color="#993333", size=5),
        legend.text = element_text(size=10),
        title = element_text(face='bold', size=10))


# Cases per Month
cleaned_df %>%
  mutate(Month = format(cleaned_df$Date, "%Y-%m")) %>%
  group_by(Month) %>%
  summarize(Cases = n()) %>%
  ggplot(aes(x = Month, y = Cases))+
  geom_point(size=.3, color='blue')+
  geom_line(group=1, color='blue')+
  ggtitle('Shooting Incidents Per Month')+
  xlab('Months')+p


# Cases and Deaths per month
cleaned_df %>%
  mutate(Month = format(cleaned_df$Date, "%Y-%m")) %>%
  group_by(Month) %>%
  summarise(Cases = n(), Deaths = sum(Murdered)) %>%
  filter(Cases > 0 & Deaths > 0) %>%
  ggplot(aes(x = Month, y= Cases))+
  geom_line(aes(group = 1, color='Cases')) +
  geom_point(aes(color='Cases')) +
  geom_line(aes(y=Deaths, group = 2, color='Deaths')) +
  geom_point(aes(y=Deaths, color='Deaths'))+ p


# Cases by Area
cleaned_df %>%
  mutate(Month = format(cleaned_df$Date, "%Y-%m")) %>%
  group_by(Month, Area) %>%
  summarise(Cases = n()) %>%
  filter(Cases > 0) %>%
  ggplot(aes(x = Month, y = Cases, col = Area, group = Area))+
  geom_point(size=1)+
  geom_line()+
  geom_smooth()+
  ggtitle('Monthly Shooting Cases per Area')+
  xlab('Months') +p


cleaned_df %>%
  mutate(Month = format(cleaned_df$Date, "%Y-%m")) %>%
  group_by(Month, Area) %>%
  summarise(Cases = n()) %>%
  ggplot(aes(x = Month, y = Cases, col = Area, group = Area))+
  geom_smooth()+
  ggtitle('Monthly Shooting Cases per Area')+
  xlab('Months') + p

# By age groups
cleaned_df %>%
  group_by(PERP_AGE_GROUP, VIC_AGE_GROUP) %>%
  summarise(Cases=n(), Deaths=sum(Murdered)) %>%
  ggplot(aes(x = VIC_AGE_GROUP, y = PERP_AGE_GROUP, col=Deaths))+
  geom_count(aes(col=Deaths, size = Cases)) +
  scale_size_area(max_size = 15) +
  scale_colour_gradient(low="blue", high="red")+
  xlab('Victim Age Group')+
  ylab('Perp Age Group') + p

library(tidyr)
# By age groups and Area
cleaned_df %>%
  group_by(Area, PERP_AGE_GROUP, VIC_AGE_GROUP) %>%
  summarise(Cases=n(), Deaths=sum(Murdered)) %>%
  ggplot(aes(x = VIC_AGE_GROUP, y = PERP_AGE_GROUP, col=Deaths))+
  geom_count(aes(col=Deaths, size = Cases)) +
  scale_size_area(max_size = 10) +
  scale_colour_gradient(low="blue", high="red")+
  facet_grid(Area~.) + 
  xlab('Victim Age Group')+
  ylab('Perp Age Group') + p

# Cases and Deaths by Perp Race
cleaned_df %>%
  group_by(PERP_RACE) %>%
  summarise(Cases=n(), Deaths=sum(Murdered)) %>%
  gather(key = var, value = value, Cases, Deaths) %>%
  ggplot(color='black', aes(x = PERP_RACE, y = value, fill = var)) +
  geom_col(group=1, position='dodge', color='black') + 
  xlab('Perp Race')+
  ylab('Cases') +
  theme(axis.text.x = element_text(color="#993333", size=5),
        axis.text.y = element_text(face="bold", color="#993333", size=5),
        legend.text = element_text(size=10),
        legend.title = element_blank(),
        title = element_text(face='bold', size=10))

# Cases and Deaths By Area and Perp Race
cleaned_df %>%
  group_by(Area, PERP_RACE) %>%
  summarise(Cases=n(), Deaths=sum(Murdered)) %>%
  gather(key = var, value = value, Cases, Deaths) %>%
  ggplot(aes(x = PERP_RACE, y = value, fill = var)) +
  geom_bar(stat = 'identity', position='dodge', color='black')+
  facet_grid(Area~.) + 
  xlab('Perp Race')+
  ylab('Cases') +
  theme(axis.text.x = element_text(color="#993333", size=5),
        axis.text.y = element_text(face="bold", color="#993333", size=5),
        legend.text = element_text(size=10),
        legend.title = element_blank(),
        title = element_text(face='bold', size=10))








  
  

