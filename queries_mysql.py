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
    create or replace view player_summary as
    with t1 as (
        select
            p.id as player_id,
            p.name, 
            p.elo,
            s.accuracy,
            s.score,
            s.points,
            g.id as game_id,
            m.id as match_id,
            s.position,
        dense_rank() over (
            partition by p.id 
            order by m.start_time desc
        ) rnk
        from player p
        left join score s on p.id = s.player_id
        left join game g on s.game_id = g.id
        left join `match` m on g.match_id = m.id
    )
    select 
        player_id as id,
        name,
        elo,
        coalesce(sum(score), 0) as total_score,
        coalesce(round(sum(points), 2), 0) as total_points,
        count(game_id) as maps_played,
        count(distinct match_id) as matches_played,
        coalesce(round(avg(position), 2), 0) as average_position,
        coalesce(round(avg(score), 2), 0) as average_score,
        coalesce(round(sum(accuracy * POW(0.95, (rnk - 1))) / sum(POW(0.95, (rnk - 1))), 4), 0) as average_accuracy,
        rank() over (
        order by elo desc
        ) player_rank
    from 
        t1
    group by 
        id;'''