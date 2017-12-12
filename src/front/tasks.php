<?php
    $db = mysqli_connect(getenv('MYSQL_HOST'), getenv('MYSQL_USER'), getenv('MYSQL_PASS'), getenv('MYSQL_DB'));
    $sql = "SELECT guid, template, min(entered) FROM tasks GROUP BY guid, template ORDER BY min(entered) DESC";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    $tasks = array();
    while ($row = $query->fetch_object()) {
        $tasks[] = $row;
    }

    foreach ($tasks as &$task) {
        $sql = "SELECT min(distance) AS dist FROM matches WHERE task_id IN (SELECT task_id FROM tasks WHERE guid = '$task->guid') && distance IS NOT NULL";
        $query = $db->query($sql);
        if (!$query) echo $sql;
        $task->min_distance = $query->fetch_object()->dist;

        $stats = array();
        $sql = "SELECT count(*) as count FROM `tasks` WHERE task_id IN (SELECT task_id FROM tasks WHERE guid = '$task->guid') && started IS NULL && completed IS NULL";
        $query = $db->query($sql);
        if (!$query) echo $sql;
        while ($row = $query->fetch_object()) {
            $task->queued = $row->count;
        }

        $sql = "SELECT count(*) as count FROM `tasks` WHERE task_id IN (SELECT task_id FROM tasks WHERE guid = '$task->guid') && started IS NOT NULL && completed IS NULL";
        $query = $db->query($sql);
        if (!$query) echo $sql;
        while ($row = $query->fetch_object()) {
            $task->processing = $row->count;
        }

        $sql = "SELECT count(*) as count FROM `tasks` WHERE task_id IN (SELECT task_id FROM tasks WHERE guid = '$task->guid') && started IS NOT NULL && completed IS NOT NULL";
        $query = $db->query($sql);
        if (!$query) echo $sql;
        while ($row = $query->fetch_object()) {
            $task->completed = $row->count;
        }
    }

    $sql = "SELECT count(*) AS total, round(avg(timediff(completed,  started) / 60)) as minutes, host FROM `tasks` WHERE host IS NOT NULL GROUP BY host ORDER BY count(*) DESC";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    $hosts = array();
    while ($row = $query->fetch_object()) {
        $hosts[] = $row;
    }
?>
<html>
<head>
    <title>All Tasks</title>

    <style>
        body {
            font-family: Verdana, Geneva, sans-se
        }

        .meta {
            float: left;
            padding: 5px;
            vertical-align: top;
        }

        .task-image, .template-image {
            float: left;
        }

    </style>
</head>
<body>
    <?php foreach ($hosts as $host): ?>
        <?=$host->host?>: <?=$host->total?> / <?=$host->minutes?> min avg<br />
    <?php endforeach; ?>
    <hr />
    <?php foreach ($tasks as $task): ?>
        <div class="row" style="clear: both; ">
            <a href="/view_task.php?guid=<?=$task->guid?>&distance=10"><img src="/data/templates/<?=$task->template?>" width="150" style="float: left; padding: 15px;" /></a><br />
            Minimum Distance: <?=$task->min_distance?><br />
            Queued: <?=$task->queued?><br />
            Processing: <?=$task->processing?><br />
            Completed: <?=$task->completed?><br />
        </div>
    <?php endforeach; ?>
</body>
</html>
