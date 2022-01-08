drop_match_summary_table = 'drop table if exists match_summary'
create_match_summary_view = f'''
    create or replace view match_summary
    as
    select
        coalesce(player.id, 277063) as player_id,
        `match`.id as match_id,
        elo_history.id as elo_id,
        coalesce(player.name, "Abandoned Match") as player_name,
        `match`.name as match_name,
        coalesce(sum(score.score), 727) as total_score,
        coalesce(sum(score.points), 727) as total_points,
        coalesce(round(avg(score.position), 2), 727) as average_position,
        coalesce(round(avg(score.score), 2), 727) as average_score,
        coalesce(round(avg(score.accuracy), 4), 727) as average_accuracy,
        coalesce(elo_history.old_elo, 727) as old_elo,
        coalesce(elo_history.new_elo, 727) as new_elo,
        coalesce(elo_history.elo_change, 727) as elo_change
    from 
        `match` left join game on `match`.id = game.match_id
        left join score on game.id = score.game_id
        left join player on player.id = score.player_id
        left join elo_history on (`match`.id = elo_history.match_id and player.id = elo_history.player_id)
    group by player.id, `match`.id, elo_history.id;
    '''
drop_player_summary_table = 'drop table if exists player_summary'
create_player_summary_view = f'''
    CREATE OR REPLACE VIEW player_summary
    as
    WITH t1 AS (
        SELECT 
            p.id AS player_id,
            p.name AS name,
            p.elo AS elo,
            s.accuracy AS accuracy,
            s.score AS score,
            s.points AS points,
            g.id AS game_id,
            m.id AS match_id,
            s.position AS position,
            RANK() OVER (
                PARTITION BY p.id 
                ORDER BY m.start_time 
                desc 
            )  AS rnk,
            m.start_time as match_start
        FROM 
            player p 
            LEFT JOIN score s ON p.id = s.player_id 
            LEFT JOIN game g ON s.game_id = g.id
            LEFT JOIN `match` m ON g.match_id = m.id
    ) 
    SELECT 
        t1.player_id AS id,
        t1.name AS name,
        t1.elo AS elo,
        coalesce(SUM(t1.score),0) AS total_score,
        coalesce(round(SUM(t1.points),2),0) AS total_points,
        count(t1.game_id) AS maps_played,count(DISTINCT t1.match_id) AS matches_played,
        coalesce(round(avg(t1.position),2),0) AS average_position,
        coalesce(round(avg(t1.score),2),0) AS average_score,
        coalesce(round((SUM((t1.accuracy * pow(0.95,(t1.rnk - 1)))) / SUM(pow(0.95,(t1.rnk - 1)))),4),0) AS average_accuracy,
        rank() OVER (ORDER BY t1.elo desc )  AS player_rank,
        coalesce(timestampdiff(day, max(match_start), current_timestamp()), 9999) as last_played_days
    FROM t1
    GROUP BY id;'''