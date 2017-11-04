<?php
    function getTS($filename) {
        list($frame, $ext) = explode('.', $filename);

        $ts = stdClass;
        $ts->frame = $frame;
        $ts->m = intdiv($frame, 60);
        $ts->s = $frame % 60;

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
        $task[$row->task_id] = $row;
        $task_ids[] = $row->task_id;
    }

    sort($task_ids);

    $ids = "'" . implode("', '", $task_ids) . "'";

    $sql = "SELECT * FROM image_matches_bf WHERE task_id IN ($ids) && distance < $distance ORDER BY video_id, filename";
    $query = $db->query($sql);
    if (!$query) echo $sql;
?>

<a href="/new_task.php">New Task</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance-1?>">Decrease Distance</a> | <a href="?guid=<?=$guid?>&distance=<?=$distance+1?>">Increase Distance</a>

<hr />

<img src="/templates/<?=$guid?>.jpg" width="400"/>

<?php while ($row = $query->fetch_object()): $ts = getTS($row->filename); ?>
    <a href="https://youtu.be/<?=$row->video_id?>?t=<?=$ts->m?>m<?=$ts->s?>s" target="_video"><img src="/data/frames/<?=$row->video_id?>/<?=$row->filename?>" width="200" /></a>
<?php endwhile; ?>
