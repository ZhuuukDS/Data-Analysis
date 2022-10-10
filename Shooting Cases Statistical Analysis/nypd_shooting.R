library(ggplot2)
library(dplyr)
library(lubridate)

original_data <- read.csv('https://data.cityofnewyork.us/api/views/833y-fsy8/rows.csv?accessType=DOWNLOAD')
str(original_data)

df <- select(original_data, -c(INCIDENT_KEY, OCCUR_TIME, PRECINCT, JURISDICTION_CODE, LOCATION_DESC, X_COORD_CD, Y_COORD_CD, Latitude, Longitude, Lon_Lat))
df <- rename(df, Date = OCCUR_DATE, Area = BORO, Murdered = STATISTICAL_MURDER_FLAG)
df$Date <- mdy(df$Date)
df$Area <- factor(df$Area)
df <- mutate(df, Murdered = if_else(Murdered == 'true', 1, 0))
df$PERP_AGE_GROUP[df$PERP_AGE_GROUP == ''] <- 'UNKNOWN'
df$PERP_AGE_GROUP[df$PERP_AGE_GROUP == '224'] <- 'UNKNOWN'
df$PERP_AGE_GROUP[df$PERP_AGE_GROUP == '1020'] <- 'UNKNOWN'
df$PERP_AGE_GROUP[df$PERP_AGE_GROUP == '940'] <- 'UNKNOWN'
df$PERP_AGE_GROUP <- factor(df$PERP_AGE_GROUP)
df$PERP_SEX[df$PERP_SEX == ''] <- 'UNKNOWN'
df$PERP_SEX <- factor(df$PERP_SEX)
df$PERP_RACE[df$PERP_RACE == ''] <- 'UNKNOWN'
df$PERP_RACE <- factor(df$PERP_RACE)
df$VIC_AGE_GROUP <- factor(df$VIC_AGE_GROUP)
df$VIC_SEX <- factor(df$VIC_SEX)
df$VIC_RACE <- factor(df$VIC_RACE)

str(df)


df1 <- original_data
df1 <- df1 %>%
  select(-c(INCIDENT_KEY, OCCUR_TIME, PRECINCT, JURISDICTION_CODE, LOCATION_DESC, X_COORD_CD, Y_COORD_CD, Latitude, Longitude, Lon_Lat)) %>%
  rename(Date = OCCUR_DATE, Area = BORO, Murdered = STATISTICAL_MURDER_FLAG) %>%
  mutate(Murdered = if_else(Murdered == 'true', 1, 0),
         PERP_SEX = if_else(PERP_SEX == '', 'UNKNOWN', PERP_SEX),
         PERP_RACE = if_else(PERP_RACE == '', 'UNKNOWN', PERP_RACE),
         PERP_AGE_GROUP = if_else(PERP_AGE_GROUP %in% c('', '224', '1020', '940'), 'UNKNOWN', PERP_AGE_GROUP))
  
df1$PERP_RACE[df1$PERP_RACE == 'AMERICAN INDIAN/ALASKAN NATIVE'] <- 'AM. INDIAN/ALASKAN'
df1$VIC_RACE[df1$VIC_RACE == 'AMERICAN INDIAN/ALASKAN NATIVE'] <- 'AM. INDIAN/ALASKAN'

df1$Date <- mdy(df1$Date)
cols <- c('Area', 'PERP_AGE_GROUP','PERP_SEX', 'PERP_RACE', 'VIC_AGE_GROUP', 'VIC_SEX', 'VIC_RACE')
df1[cols] <- lapply(df1[cols], factor)



df_by_area <- df1 %>%
  group_by(Area, Date) %>%
  summarise(Cases=n(), Deaths=sum(Murdered))


df_age_groups <- df1 %>%
  group_by(PERP_AGE_GROUP, VIC_AGE_GROUP) %>%
  summarise(Cases=n(), Deaths=sum(Murdered))

sum(df_age_groups$Cases)

ggplot(df_age_groups, aes(x = VIC_AGE_GROUP, y = PERP_AGE_GROUP, col=Deaths))+
  geom_count(aes(col=Deaths, size = Cases)) +
  scale_size_area(max_size = 15) +
  scale_colour_gradient(low="blue", high="red")


df_age_groups_areas <- df1 %>%
  group_by(Area, PERP_AGE_GROUP, VIC_AGE_GROUP) %>%
  summarise(Cases=n(), Deaths=sum(Murdered))

sum(df_age_groups_areas$Cases)

ggplot(df_age_groups_areas, aes(x = VIC_AGE_GROUP, y = PERP_AGE_GROUP, col=Deaths))+
  geom_count(aes(col=Deaths, size = Cases)) +
  scale_size_area(max_size = 10) +
  scale_colour_gradient(low="blue", high="red")+
  facet_grid(Area~.)


deaths_by_area_perp_race <- df1 %>%
  group_by(Area, PERP_RACE) %>%
  summarise(Cases=n(), Deaths=sum(Murdered))

sum(deaths_by_area_perp_race$Cases)

ggplot(deaths_by_area_perp_race, aes(PERP_RACE, Cases))+
  geom_bar(stat='identity')+
  ylim(c(0, 11500))

library(tidyr)

df_long <- gather(deaths_by_area_perp_race, key = var, value = value, Cases, Deaths)

ggplot(df_long, aes(x = PERP_RACE, y = value, fill = var)) +
  geom_col(group=1, position='dodge')

ggplot(df_long, aes(x = PERP_RACE, y = value, fill = var)) +
  geom_bar(stat = 'identity', position='dodge', color='black')+
  facet_grid(Area~.)





sum(deaths_by_area_perp_race[deaths_by_area_perp_race$PERP_RACE=='UNKNOWN',]$Cases)
sum(deaths_by_area_perp_race[deaths_by_area_perp_race$PERP_RACE=='UNKNOWN',]$Deaths)


sum(deaths_by_area_perp_race$Cases)
sum(df_long$value)
sum(df_long[df_long$PERP_RACE=='UNKNOWN',]$value)


library(tidyr)










df1 <- df_by_area

df2$Date <- format(df2$Date, "%Y-%m")


head(df1)

df2 <- df_by_area %>%
  group_by(Area, Date) %>%
  summarise(Cases=sum(Cases))

ggplot(df2, aes(x = Date, y = Cases, col = Area, group = Area))+
  geom_point(size=.3)+
  facet_grid(Area ~ .)






summary(df$PERP_AGE_GROUP)
summary(df$VIC_AGE_GROUP)

count(df[df$VIC_AGE_GROUP=='UNKNOWN',])
count(df[df$VIC_AGE_GROUP=='UNKNOWN' & df$MURDERED == 'Y',])













## Modeling data

# The main idea is to calculate the odds of being murdered during the shooting incidents depending 
# on the predictors in the original data. 
# Here we will not count the probability to get into an incident, as the number of cases depending on the area
# was clearly seen earlier. We will focus on the model showing what factors significantly change the chances 
# to be killed. 
# So, let's first put some nominative predictors from original data into a separate data frame to make a logistic regression.


df_for_models <- cleaned_df %>%
  filter(VIC_AGE_GROUP != 'UNKNOWN', PERP_AGE_GROUP != 'UNKNOWN', VIC_SEX != 'U') %>%
  mutate(Murdered = factor(if_else(Murdered == 1, 'Y', 'N'))) %>%
  select(Murdered, Area, VIC_SEX, VIC_AGE_GROUP, PERP_AGE_GROUP)


df_for_models$VIC_SEX <- droplevels(df_for_models$VIC_SEX)
df_for_models$VIC_AGE_GROUP <- droplevels(df_for_models$VIC_AGE_GROUP)
df_for_models$PERP_AGE_GROUP <- droplevels(df_for_models$PERP_AGE_GROUP)

# So, here we look at the cases indicated with murdered flag which include 
# sex and age group of both perp and victim, and also an Area where an incident occured

summary(df_for_models)

# Let's take an intercept only model
simple_fit <- glm(Murdered ~ 1, df_for_models, family = "binomial")
coef(simple_fit)
summary(simple_fit)

# This negative number is a log of odds of being murdered in a shooting incident 
# regardless of any other influencing factors.
# In other words this the log of a fraction of total murders and incidents
table(df_for_models$Murdered)
odds <- 3100 / 9946
log(odds) 

# Let's take a look on a logistic regression where a dependent variable is a 
# factor 'Murdered' depends on all other predictors

fits <- glm(Murdered ~ . , df_for_models, family = "binomial")
summary(fits)
anova(fits, test="Chisq")

# First, we see that this model significantly improves our intercept only model.
# Also, we can see that victim sex and area don't have an impact on the model, 
# whereas age groups of both perps and victims have a significant influence.
# Indeed, if we look at the mosaic plot, we can see that although the amount of
# cases and deaths of males and females vary a lot, the incident-murders ratio 
# remains almost the same in Bronx, Brooklyn and Manhattan for both genders.

mosaic(Murdered ~ VIC_SEX | Area, data=df_for_models,
       highlighting_fill = c("lightblue", "pink"),
       labeling = labeling_border(rot_labels = c(0), 
                                  gp_labels = gpar(fontsize = 6),
                                  set_varnames = c(VIC_SEX="Gender"),
                                  gp_varnames = gpar(fontsize = 10)
                                  )
       )


# The most interesting observations are in age groups

mosaic(Murdered ~ PERP_AGE_GROUP | VIC_AGE_GROUP, data=df_for_models,
       highlighting_fill = c("lightblue", "pink"),
       labeling = labeling_border(rot_labels = c(0), 
                                  gp_labels = gpar(fontsize = 6),
                                  set_varnames = c(PERP_AGE_GROUP='Perpetrator Age', VIC_AGE_GROUP='Victim Age'),
                                  gp_varnames = gpar(fontsize = 10)
       ))

# Moreover, although the area of an incident doesn't significantly impacts on the odds
# of being killed, we can see below that perps and victims of different age group
# have different case-death ratio depending on the region

mosaic(Murdered ~ VIC_AGE_GROUP | Area, data=df_for_models)
mosaic(Murdered ~ PERP_AGE_GROUP | Area, data=df_for_models)

# All of these observations have to be analyzed and checked.

# First let's prove that victim sex is not statistically significant and it
# doesn't improve our model:

fit_sex <- glm(Murdered ~ VIC_SEX, df_for_models, family = "binomial")
coef(fit_sex)
summary(fit_sex)
table(df_for_models$Murdered, df_for_models$VIC_SEX)
anova(simple_fit, fit_sex, test="Chisq")

# Then, let's prove that age groups of both perps and victims significantly improve
# our model
fit_vic_age <- glm(Murdered ~ VIC_AGE_GROUP, df_for_models, family = "binomial")
coef(fit_vic_age)
summary(fit_vic_age)
table(df_for_models$Murdered, df_for_models$VIC_AGE_GROUP)
anova(simple_fit, fit_vic_age, test="Chisq")
mosaic(Murdered ~ VIC_AGE_GROUP, data=df_for_models)


fit_perp_age <- glm(Murdered ~ PERP_AGE_GROUP, df_for_models, family = "binomial")
coef(fit_perp_age)
summary(fit_perp_age)
table(df_for_models$Murdered, df_for_models$PERP_AGE_GROUP)
anova(simple_fit, fit_perp_age, test="Chisq")

# And also the model with two categorial predictors of age groups significantly important 

fit_ages <- glm(Murdered ~ VIC_AGE_GROUP * PERP_AGE_GROUP, df_for_models, family = "binomial")
coef(fit_ages)
summary(fit_ages)
anova(simple_fit, fit_ages, test="Chisq")
mosaic(Murdered ~ VIC_AGE_GROUP | PERP_AGE_GROUP, data=df_for_models)

# Then, we can have a logistic regression depending on an area predictor.
# Overall, this model doesn't have a significant improvement compared to intercept only model,
# however we see that changing to some areas may influence on estimated odds.
fit_area <- glm(Murdered ~ Area, df_for_models, family = "binomial")
coef(fit_area)
summary(fit_area)
table(df_for_models$Murdered, df_for_models$Area)
anova(simple_fit, fit_area, test="Chisq")

# So, let's try a model with two predictors - age group of perp and Area with their 
# dependencies. And that works fine.

fit_perp_age_area <- glm(Murdered ~ PERP_AGE_GROUP * Area, df_for_models, family = "binomial")
coef(fit_perp_age_area)
summary(fit_perp_age_area)
anova(simple_fit, fit_perp_age_area, test="Chisq")


## Finally, our model will include victim age group, perp age group, area and their dependencies:

fit_long <- glm(Murdered ~ VIC_AGE_GROUP + PERP_AGE_GROUP * Area, df_for_models, family = "binomial")
summary(fit_long)
anova(fit_long, test="Chisq")

# Bases on this model let's make some predictions.
# First, let's imagine that a shooting accident occured in Manhattan area, victim is 
# less than 18 y.o. and perp is also less than 18 y.o. Seems that would be a scenario, when
# a victim has maximum chances to stay alive.
new_df_min <- data.frame(VIC_SEX = 'M', 
                     VIC_AGE_GROUP = "<18", 
                     PERP_AGE_GROUP = "<18", Area = 'STATEN ISLAND')
predict(fit_long, newdata = new_df_min, type = "response")

# And otherwise, if an accident is in Staten Island and both victim and perp are 
# older than 65, then there are least chances for a victim to stay alive.
new_df_max <- data.frame(VIC_SEX = 'M', 
                         VIC_AGE_GROUP = "65+", 
                         PERP_AGE_GROUP = "65+", Area = 'STATEN ISLAND')
predict(fit_long, newdata = new_df_max_long, type = "response")


