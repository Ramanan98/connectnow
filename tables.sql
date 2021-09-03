-- Used tables
create table user_profiles(user_id int, username varchar, birthday date, state varchar,isOnline bool);
create table interests(user_id int, tags text[]);
create table user_preferences(user_id int, age_min int, age_max int, state varchar);

create or replace function get_matching_users(current_user_id int) returns table(match_id int) as $$
declare
   search_state varchar;
   search_age_min int; 
   search_age_max int;
begin 
   select state into search_state from user_preferences where user_id = current_user_id;
   select age_min into search_age_min from user_preferences where user_id = current_user_id;
   select age_max into search_age_max from user_preferences where user_id = current_user_id;
   return query
   select user_id from user_profiles where state = search_state and extract(year from age(current_date,birthday)) >= search_age_min and extract(year from age(current_date,birthday)) <=search_age_max and isOnline = '1' and user_id != current_user_id;
end;
$$ language plpgsql;


select * from user_profiles order by user_id asc;
select * from interests order by user_id asc;
select * from user_preferences order by user_id asc;

/*For data only, DO NOT USE THESE to create users. Use create_users.py file to create users
user_id is added from auth_user table (in db_handle.py), no need to add it manually

insert into user_profiles(user_id,name,birthday,gender,bio,state,education,employment,isOnline) values ('Tim','1998-6-10','m','abc','Tamil Nadu','B.Tech','Student','1');
insert into user_profiles(user_id,name,birthday,gender,bio,state,education,employment,isOnline) values ('Ana','1999-6-10','f','xyz','Uttarakhand','B.Tech','Engineer','1');
insert into user_profiles(user_id,name,birthday,gender,bio,state,education,employment,isOnline) values ('Rob','1998-1-6','m','qwe','Karnataka','12th','Student','0');
insert into user_profiles(user_id,name,birthday,gender,bio,state,education,employment,isOnline) values ('Rebecca','1999-8-3','f','rty','Delhi','B.Com','Analyst','1');
insert into user_profiles(user_id,name,birthday,gender,bio,state,education,employment,isOnline) values ('Dave','1999-12-12','m','uio','Kerala','10th','Student','0');
insert into user_profiles(user_id,name,birthday,gender,bio,state,education,employment,isOnline) values ('Tom','2000-12-12','m','azw','Uttarakhand','B.A.','Student','1');

insert into interests values(ARRAY['technology','programming','nature','food','books']);
insert into interests values(ARRAY['technology','programming','travel','food','books']); 
insert into interests values(ARRAY['luxury','music','nature','food','books']); 
insert into interests values(ARRAY['cinephile','luxury','music','food','books']); 
insert into interests values(ARRAY['cinephile','luxury','music','blogging','fashion']);
insert into interests values(ARRAY['technology','programming','nature','food','books']);

insert into user_preferences values(18,25,'Uttarakhand');
insert into user_preferences values(19,24,'Tamil Nadu');
insert into user_preferences values(19,23,'Karnataka');
insert into user_preferences values(18,23,'Delhi');
insert into user_preferences values(18,24,'Tamil Nadu');

*/

create or replace function get_matching_users(current_user_id int) returns table(match_id int) as $$
declare
   search_state varchar;
   search_age_min int; 
   search_age_max int;
begin 
   select state into search_state from user_preferences where user_id = current_user_id;
   select age_min into search_age_min from user_preferences where user_id = current_user_id;
   select age_max into search_age_max from user_preferences where user_id = current_user_id;
   return query
   select user_id from user_profiles where state = search_state and extract(year from age(current_date,birthday)) >= search_age_min and extract(year from age(current_date,birthday)) <=search_age_max and isOnline = '1' and user_id != current_user_id;
end;
$$ language plpgsql;
