<?php
    $db = mysqli_connect('a01-mysql-01', 'root', 'q1w2e3r4', 'image_match');
    $guid = mysqli_real_escape_string($db, $_GET['guid']);
    $distance = isset($_GET['guid']) ? (int)$_GET['guid'] : 26;

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

    $sql = "SELECT * FROM image_matches_bf WHERE task_id IN ($ids) WHERE distance < $distance ORDER BY video_id, filename";
    $query = $db->query($sql);
    if (!$query) echo $sql;
?>

<img src="/templates/<?=$guid?>.jpg" width="400"/>

<?php while ($row = $query->fetch_object()): ?>
    <img src="/data/frames/<?=$row->video_id?>/<?=$row->filename?>" width="200" />
<?php endwhile; ?>
