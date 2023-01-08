import requests
from bs4 import BeautifulSoup
import time
from plyer import notification

def soupify_url(url):
    #type get user agent in chrome
    header = {"user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    page = requests.get(url,headers = header)
    soup = BeautifulSoup(page.content,'lxml')
    return soup

def check_recent_game(soup):
    '''
    PAST: yesterday/today : imso_mh__pst-m-stts-l --> child div "imso-hide-overflow"  --> last span child ka text
    FUTURE: tomorrow/today: imso_mh__pre-m-stts imso-hide-overflow -> final span child ka text ka first part
    LIVE: ??
    '''
    today = False
    tomorrow = False
    earlier_today = False
    yesterday = False
    when = ""
    if(soup.find('div', class_="imso_mh__pre-m-stts imso-hide-overflow")):
        s = soup.find('div', class_="imso_mh__pre-m-stts imso-hide-overflow").find_all('span')
        if(len(s)>0 and "today" in s[-1].text.lower()):
            when = s[-1].text
            today = True
            
        if(len(s)>0 and "tomorrow" in s[-1].text.lower()):
            when = s[-1].text
            tomorrow = True
            
    if(soup.find('div', class_="imso_mh__pst-m-stts-l") and soup.find('div', class_="imso_mh__pst-m-stts-l").find('div',
        class_="imso-hide-overflow")):
        s = soup.find('div', class_="imso_mh__pst-m-stts-l").find('div',
        class_="imso-hide-overflow").find_all('span')
        if(len(s)>0 and "today" in s[-1].text.lower()):
            when = s[-1].text
            earlier_today = True
        if(len(s)>0 and "yesterday" in s[-1].text.lower()):
            when = s[-1].text
            yesterday = True
    return [today, tomorrow, earlier_today, yesterday, when]

def check_game_time(soup):
    ## check full time
    ft_label_matched = soup.find("span", class_="imso_mh__ft-mtch imso-medium-font imso_mh__ft-mtchc")
    ft_text = None
    if ft_label_matched:
        ft_text = ft_label_matched.text
    
    ## check half time
    ht_label_matched = soup.find('div',class_="imso_mh__lv-m-stts-cont")
    ht_text = None
    if ht_label_matched:
        ht_text = ht_label_matched.text
    
    ## check live
    live_label_matched = soup.find('span',class_="liveresults-sports-immersive__game-minute")
    live_text = None
    if live_label_matched:
        live_text = live_label_matched.text

    return [ft_text, ht_text, live_text]

def get_team_names(soup):
    # team on left
    l_team_div = soup.find('div', class_="imso_mh__first-tn-ed imso_mh__tnal-cont imso-tnol")
    l_team_name = l_team_div.span.text

    # team on right
    r_team_div = soup.find('div', class_="imso_mh__second-tn-ed imso_mh__tnal-cont imso-tnol")
    r_team_name = r_team_div.span.text

    return [l_team_name, r_team_name]

def get_team_scores(soup):
    #score of team on left
    l_team_score_div = soup.find('div', class_="imso_mh__l-tm-sc imso_mh__scr-it imso-light-font")
    l_team_score = 0
    if l_team_score_div:
        l_team_score = l_team_score_div.text
    
    
    
    #score of team on right
    r_team_score_div = soup.find('div', class_="imso_mh__r-tm-sc imso_mh__scr-it imso-light-font")
    r_team_score = 0
    if r_team_score_div:
        r_team_score = r_team_score_div.text

    return [l_team_score, r_team_score]

def get_todays_score(team):
    ##
    URL = f"https://www.google.com/search?q={team}"
    soup = soupify_url(URL)
    
    today, tomorrow, earlier_today, yesterday, when = check_recent_game(soup);
    if(not(today or tomorrow or earlier_today or yesterday)):
        print('No recent games of your team!')
        return None;
    
    ft_text, ht_text, live_text = check_game_time(soup)
    if(not(ft_text or ht_text or live_text)):
        print('No recent games of your team!')
        return None;

    l_team_name, r_team_name = get_team_names(soup)
    l_team_score, r_team_score = get_team_scores(soup)
    
    # need to remove special characters
    when = when.encode("ascii", "replace").decode(encoding="utf-8", errors="ignore").replace("?","")

    return [when, l_team_name, l_team_score, r_team_name, r_team_score]

def notify(arr):
    print(arr)
    if arr is None:
        return
    notification.notify(
        title = "Game",
        message = f"{arr[0]} {arr[1]} - {arr[3]} {arr[2]}",
    #     app_icon = "data//football.ico",
        timeout = 10
    )


# team = input("Enter the team name : ").lower().split()
# team = "+".join(team)
team = "manchester+united"
team = "chelsea" # wrong result 
team = "manchester+city" # wrong result 
#team = "los+angeles+lakers"
#team = "sacramento+kings"
notify(get_todays_score(team))