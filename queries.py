drop_match_summary_table = 'drop table if exists match_summary'
create_match_summary_view = f'''
    create or replace view match_summary
    as 
    select
    player.id as player_id,
    match.id as match_id,
    player.name as player_name,
    sum(score.score) as total_score, 
    round(cast(avg(score.position) as numeric), 2) as average_position,
    round(cast(avg(score.score) as numeric), 2) as average_score,
    round(cast(avg(score.accuracy) as numeric), 2) as average_accuracy
    from match INNER join game on match.id = game.match_id
    inner join score on game.id = score.game_id 
    inner join player on player.id = score.player_id
    group by player.id, match.id;
    '''