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

    $db = mysqli_connect('a01-mysql-01', 'root', 'q1w2e3r4', 'image_match');
    $guid = mysqli_real_escape_string($db, $_GET['guid']);
    $distance = isset($_GET['distance']) ? (int)$_GET['distance'] : 26;

    $sql = "SELECT * FROM tasks WHERE guid = '$guid'";
    $query = $db->query($sql);

    $tasks = array();
    $task_ids = array();
    while ($row = $query->fetch_object()) {
        $tasks[$row->task_id] = $row;
        $tasks[$row->task_id]['matches'] = array();
        $task_ids[] = $row->task_id;
    }

    sort($task_ids);

    $ids = "'" . implode("', '", $task_ids) . "'";

    $sql = "SELECT * FROM image_matches_bf WHERE task_id IN ($ids) && distance < $distance ORDER BY video_id, filename";
    $query = $db->query($sql);
    if (!$query) echo $sql;
    while ($row = $query->fetch_object()) {
        $match = $row;
        $ts = getTS($row->filename);
        $match->m = $ts->m;
        $match->s = $ts->s;
        $tasks[$row->task_id]['matches'][] = $row;
    }
?>

<a href="/new_task.php">New Task</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance-1?>">Decrease Distance</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance+1?>">Increase Distance</a>

<hr />

<img src="/templates/<?=$guid?>.jpg" width="400"/>

<?php foreach ($tasks as $task: ?>
    <?php foreach ($task->matches as $match: ?>
        <a href="https://youtu.be/<?=$match->video_id?>?t=<?=$match->m?>m<?=$match->s?>s" target="_video"><img src="/data/frames/<?=$match->video_id?>/<?=$match->filename?>" width="200" /></a>
    <?php endforeach; ?>
<?php endforeach; ?>
