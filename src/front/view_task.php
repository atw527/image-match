<?php
    function getTS($filename) {
        list($frame, $ext) = explode('.', $filename);

        $seconds = floor($frame / 10);

        $ts = new stdClass();
        $ts->frame = $seconds;
        $ts->m = intdiv($seconds, 60);
        $ts->s = $seconds % 60;

        return $ts;
    }

    $db = mysqli_connect(getenv('MYSQL_HOST'), getenv('MYSQL_USER'), getenv('MYSQL_PASS'), getenv('MYSQL_DB'));
    $guid = mysqli_real_escape_string($db, $_GET['guid']);
    $distance = isset($_GET['distance']) ? (int)$_GET['distance'] : 26;

    $sql = "SELECT * FROM tasks WHERE guid = '$guid'";
    $query = $db->query($sql);

    $tasks = array();
    $task_ids = array();
    while ($row = $query->fetch_object()) {
        $tasks[$row->task_id] = $row;
        $tasks[$row->task_id]->matches = array();
        $task_ids[] = $row->task_id;
    }

    sort($task_ids);

    $ids = "'" . implode("', '", $task_ids) . "'";

    $sql = "SELECT * FROM matches WHERE task_id IN ($ids) && distance < $distance ORDER BY video_id, filename";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    while ($row = $query->fetch_object()) {
        $match = $row;
        $ts = getTS($row->filename);
        $match->m = $ts->m;
        $match->s = $ts->s;
        $tasks[$row->task_id]->matches[] = $match;
    }

    $sql = "SELECT count(*) as count, host FROM `tasks` WHERE guid = '$guid' GROUP BY host";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    $hosts = array();
    while ($row = $query->fetch_object()) {
        $hosts[] = array('count' => $row->count, 'host' => $row->host);
    }

    $sql = "SELECT video_id, min(distance) as min_dist FROM matches WHERE task_id IN ($ids) && distance < 10 GROUP BY task_id, video_id ORDER BY min_dist";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    $bests = array();
    while ($row = $query->fetch_object()) {
        $bests[] = $row->video_id;
    }

    $stats = array();
    $sql = "SELECT count(*) as count FROM `tasks` WHERE task_id IN ($ids) && started IS NULL && completed IS NULL";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    while ($row = $query->fetch_object()) {
        $stats['queued'] = $row->count;
    }

    $sql = "SELECT count(*) as count FROM `tasks` WHERE task_id IN ($ids) && started IS NOT NULL && completed IS NULL";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    while ($row = $query->fetch_object()) {
        $stats['processing'] = $row->count;
    }

    $sql = "SELECT count(*) as count FROM `tasks` WHERE task_id IN ($ids) && started IS NOT NULL && completed IS NOT NULL";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    while ($row = $query->fetch_object()) {
        $stats['completed'] = $row->count;
    }
?>
<html>
<head>
    <title>View Task</title>

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

<a href="/tasks.php">&lt; All Tasks</a> | <a href="/new_task.php">New Task</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance-1?>">Decrease Distance</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance+1?>">Increase Distance</a>

<hr />

<img class="template-image" src="/data/templates/<?=$guid?>.jpg" width="400" />

<p class="meta">
    Status<br />
    <span class="label" style="font-weight: bold;"><?=$stats['queued']?></span><span class="value">Queued</span><br />
    <span class="label" style="font-weight: bold;"><?=$stats['processing']?></span><span class="value">Processing</span><br />
    <span class="label" style="font-weight: bold;"><?=$stats['completed']?></span><span class="value">Completed</span><br />
</p>

<p class="meta">
    Worker Host Breakdown<br />
    <?php foreach ($hosts as $host): ?>
        <span class="label" style="font-weight: bold;"><?=$host['count']?></span>
        <span class="value"><?=$host['host']?></span><br />
    <?php endforeach; ?>
</p>

<p class="meta">
    Matches < 10<br />
    <?php foreach ($bests as $best): ?>
        <a href="#<?=$best?>"><?=$best?></a> |
    <?php endforeach; ?>
</p>

<div style="clear: both; padding: 5px; "></div>

<?php foreach ($tasks as $task): ?>
    <hr style="clear: both; " />

    <a name="<?=$task->video_id?>" href="https://youtu.be/<?=$task->video_id?>" class="task-image" target="_blank"><img src="/data/video/<?=$task->video_id?>.jpg" width="300" /></a>

    <p class="meta">
        <span class="label">Started:</span> <span class="value"><?=$task->started?></span><br />
        <span class="label">Completed:</span> <span class="value"><?=$task->completed?></span><br />
        <span class="label">Worker Host:</span> <span class="value"><?=$task->task_id?> <?=$task->host?> <?=$task->container?></span><br />
        <span class="label">Video:</span> <span class="value"><?=$task->video_id?></span><br />
        <span class="label">Exceptions:</span> <span class="value"><?=$task->exceptions?></span><br />
    </p>

    <div style="clear: both; padding: 5px; "></div>

    <?php foreach ($task->matches as $match): ?>
        <a href="https://youtu.be/<?=$match->video_id?>?t=<?=$match->m?>m<?=$match->s?>s" target="_video">
            <img src="/data/frames/<?=$match->video_id?>/<?=$match->filename?>" width="200" class="dist-<?=$match->distance?>" title="Distance: <?=$match->distance?>" />
        </a>
    <?php endforeach; ?>
<?php endforeach; ?>

</body>
</html>
