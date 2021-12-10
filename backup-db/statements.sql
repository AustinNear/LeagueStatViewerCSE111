
SELECT '#1___________________________________________________';
--teams that existed in 2018
SELECT distinct(teams.teamtag)
FROM teams
WHERE teams.year = '2018';

SELECT '#2___________________________________________________';
--matches played by team C9 where 'Xayah' was picked for ADC
SELECT matches.year, matches.season, matches.type, matches.league, matches.BlueTeamTag, picks.blueADCChamp, matches.redTeamTag, picks.redADCChamp
FROM matches, picks
WHERE matches.address = picks.address AND matches.blueTeamTag = 'C9' AND picks.blueADCChamp = 'Ashe'
UNION
SELECT matches.year, matches.season, matches.type, matches.league, matches.BlueTeamTag, picks.blueADCChamp, matches.redTeamTag, picks.redADCChamp
FROM matches, picks
WHERE matches.address = picks.address AND matches.redTeamTag = 'C9' AND picks.redADCChamp = 'Ashe';

SELECT '#3___________________________________________________';
--insert new fake team
insert into teams values('FAKE', 2021, 'Fall', 'topname', 'jgname', 'midname', 'adcname', 'supname');
select *
from teams
where year between 2018 and 2021;

SELECT '#4___________________________________________________';
--update season the fake team existed in to spring
update teams
set season = 'Spring'
where teamtag = 'FAKE';
select *
from teams
where year between 2018 and 2021;

SELECT '#5___________________________________________________';
--delete fake team
delete from teams where teams.teamtag = 'FAKE';
select *
from teams
where year between 2018 and 2021;

SELECT '#6___________________________________________________';
--the classes of blue team top champion in a specific match
select champions.class
from champions, picks, matches
where champions.name = picks.bluetopchamp AND picks.address = matches.address AND matches.address = 'http://matchhistory.na.leagueoflegends.com/en/#match-details/TRLH1/30030?gameHash=fbb300951ad8327c'
;

SELECT '#7___________________________________________________';
--select every champion chosen by a specific role for a team during a given year
select picks.blueadcchamp
from picks, teams
where picks.blueteamtag = teams.teamtag and teams.year = '2018' and teams.teamtag = 'C9'
union
select picks.redadcchamp
from picks, teams
where picks.redteamtag = teams.teamtag and teams.year = '2018' and teams.teamtag = 'C9';

SELECT '#8___________________________________________________';
--show the characteristics of each champion
select * from champions;

SELECT '#9___________________________________________________';
--count every instance blue side kills a specific monster vs red side
select 'Blue', count(*) from monsters where team = 'bDragons' and type = 'ELDER_DRAGON'
union
select 'Red', count(*) from monsters where team = 'rDragons' and type = 'ELDER_DRAGON';

SELECT '#10___________________________________________________';
--show every champion with a difficulty of 1
select name from champions where difficulty = '1';

SELECT '#11___________________________________________________';
--list every type of monster
select distinct(type) from monsters;

SELECT '#12___________________________________________________';
--list who has the most kills total across the data
select killer, count(killer) from kills
group by killer
order by count(killer) desc
limit 1;

SELECT '#13___________________________________________________';
--who has the most deaths total across the data
select victim, count(victim) from kills
group by victim
order by count(victim) desc
limit 1;

SELECT '#14___________________________________________________';
--list all different structures
select distinct(type) from structures;

SELECT '#15___________________________________________________';
--list the types of matches
select distinct(type) from matches;

SELECT '#16___________________________________________________';
--the amount of wins each side have, blue and red
select 'blue', count(*)
from matches
where bResult = '1'
union
select 'red', count(*)
from matches
where rResult = '1';

SELECT '#17___________________________________________________';
--select the champion that a specific team banned first the most times
SELECT ban1,COUNT(ban1)
FROM bans, picks
where picks.blueteamtag = 'C9' and picks.address = bans.address
GROUP BY ban1
UNION
SELECT ban1,COUNT(ban1)
FROM bans, picks
where picks.redteamtag = 'C9' and picks.address = bans.address
GROUP BY ban1
ORDER BY COUNT(ban1) DESC
limit 1;

SELECT '#18___________________________________________________';
--5 longest matches
select year, league, type, season, gamelength
from matches
group by gamelength
order by gamelength DESC
limit 5;

SELECT '#19___________________________________________________';
insert into champions values(146, 'newchamp', 'warrior', 5, 5, 'P', 10, 2, 3, 6, 7);
select * from champions;

SELECT '#20___________________________________________________';
update champions
set class = 'mage'
where id = 146;
select * from champions;

SELECT '#20___________________________________________________';
delete from champions where name = 'newchamp';
select * from champions;


--the wins vs losses for a specific champion
-- select count(bwins.bresult)+count(rwins.rresult), count(blosses.bresult)+count(rlosses.rresult)
-- from (
--     select rresult
--     from picks, matches
--     where picks.redteamtag = matches.redteamtag and matches.rresult = '1' and picks.redmiddlechamp = 'Syndra'
--     ) as rwins,
--     (
--     select bresult
--     from picks, matches
--     where picks.blueteamtag = matches.blueteamtag and matches.bresult = '1' and picks.bluemiddlechamp = 'Syndra'
--     ) as bwins,
--     (
--     select rresult
--     from picks, matches
--     where picks.redteamtag = matches.redteamtag and matches.rresult = '0' and picks.redmiddlechamp = 'Syndra'
--     ) as rlosses,
--     (
--     select bresult
--     from picks, matches
--     where picks.blueteamtag = matches.blueteamtag and matches.bresult = '0' and picks.bluemiddlechamp = 'Syndra'
--     ) as blosses;
