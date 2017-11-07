#!/usr/bin/php
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "Depracated!";
sleep(1800);
die();

function stahp($signo) {
    global $db, $video_id;
    $query = "UPDATE encode SET host = null WHERE video_id = '$video_id' LIMIT 1";
    $db->query($sql);

    chdir(dirname(__FILE__));
    chdir('..');
    if ($video_id != "" && !empty($video_id)) shell_exec("rm -rf frames/$video_id");

    exit(0);
}
pcntl_signal(SIGTERM, "stahp");

/* shell hax */
shell_exec("cp /root/.ssh/id_rsa_host /root/.ssh/id_rsa");
shell_exec("chown root: /root/.ssh/id_rsa");
shell_exec("chmod 0600 /root/.ssh/id_rsa");

$db = mysqli_connect('a01-mysql-01', 'root', 'q1w2e3r4', 'image_match');
$sql = "SELECT * FROM encode WHERE host IS NULL LIMIT 1";
$query = $db->query($sql);
$row = $query->fetch_object();

echo "INIT\n";

if (!$row) {
    /* nothing is available...sleep for a while before dying because Docker will just start again */
    echo "QUEUE COMPLETE.";
    sleep(600);
    die();
}

$video_id = $row->video_id;

/* we got this! */
$hostname = file_exists('/etc/docker_hostname') ? file_get_contents('/etc/docker_hostname') : gethostname();
$sql = "UPDATE encode SET host = '$hostname' WHERE video_id = '$video_id' LIMIT 1";
$db->query($sql);

echo "Picking up $video_id\n";

chdir(dirname(__FILE__));
chdir('..');

echo shell_exec("pwd");

if ($video_id != "" && !empty($video_id)) shell_exec("rm -rf frames/$video_id");

echo "Copying MP4...\n";
shell_exec("rsync andrew@server-13:/home/andrew/go/src/github.com/atw527/image-match/data/video/$video_id* video/");
echo shell_exec("ls -alh video/$video_id.mp4");
echo "Done!\n";

echo "Rendering frames...\n";
shell_exec("mkdir frames/$video_id");
shell_exec("ffmpeg -i video/$video_id.mp4 -r 10/1 -f image2 frames/$video_id/%6d.jpg > /dev/null");
echo "Done!\n";

echo "Deduping...\n";
chdir("frames/$video_id");
$frames = scandir('.');

// remove . and .. references
array_shift($frames);
array_shift($frames);

var_dump(count($frames));

for ($x = 0; $x < count($frames) - 1; ) {
    for ($y = $x + 1; $y < count($frames); $y++) {
        $diff = shell_exec("compare -metric RMSE $frames[$x] $frames[$y] NULL: 2>&1");

        if ($diff < 5000 && $diff != 0) {
            unlink($frames[$y]);
            //echo "Deleted $frames[$y] \n";
        } else {
            $x = $y;
            break;
        }
    }
}

echo "Done!\n";

echo "Copying frames back to server-13...\n";
chdir(dirname(__FILE__));
chdir('..');
shell_exec("rsync -a frames/$video_id andrew@server-13:/home/andrew/go/src/github.com/atw527/image-match/data/frames/");
echo "Done!\n";
