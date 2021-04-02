drop_match_summary_table = 'drop table if exists match_summary'
create_match_summary_view = f'''
    create or replace view match_summary
    as
    select
    player.id as player_id,
    `match`.id as match_id,
    elo_history.id as elo_id,
    player.name as player_name,
    `match`.name as match_name,
    sum(score.score) as total_score,
    sum(score.points) as total_points,
    round(avg(score.position), 2) as average_position,
    round(avg(score.score), 2) as average_score,
    round(avg(score.accuracy), 4) as average_accuracy,
    elo_history.old_elo as old_elo,
    elo_history.new_elo as new_elo,
    elo_history.elo_change as elo_change
    from `match` INNER join game on `match`.id = game.match_id
    inner join score on game.id = score.game_id
    inner join player on player.id = score.player_id
    inner join elo_history on (`match`.id = elo_history.match_id and player.id = elo_history.player_id)
    group by player.id, `match`.id, elo_history.id;
    '''
drop_player_summary_table = 'drop table if exists player_summary'
create_player_summary_view = f'''
    create or replace view player_summary
    as
    select 
    p.id as id,
    p.name as name,
    p.elo as elo,
    sum(s.score) as total_score,
    round(sum(s.points), 2) as total_points,
    count(g.id) as maps_played,
    count(distinct m.id) as matches_played,
    round(avg(s.position), 2) as average_position,
    round(avg(s.score), 2) as average_score,
    round(avg(s.accuracy), 4) as average_accuracy,
    rank() over (
	order by p.elo desc
    ) player_rank
    from 
    player p 
    join score s on p.id = s.player_id
    join game g on s.game_id = g.id
    join `match` m on g.match_id = m.id
    group by p.id;'''